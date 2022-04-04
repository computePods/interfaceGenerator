# For file inclusion consider:
#   https://github.com/jreese/markdown-pp
import click
import copy
import cpig.loadInterface
import cpig.generateCode
import datamodel_code_generator
import json
import os
import sys
import yaml

def loadConfig(configFile, verbose) :
  config = {
    'options' : {
      'distDir'             : 'dist',
      'interfacesDir'       : 'interfaces',
      'outputPathTemplates' : {
        'pydantic'              : [ 'python', '{}.py' ],
        'ajv'                   : [ 'js',     '{}_ajv.mjs' ],
        'pythonExamples'        : [ 'python', '{}Examples.py' ],
        'javaScriptExamples'    : [ 'js',     '{}Examples.mjs' ],
        'httpRouteUtils'        : [ 'js',     '{}HttpRouteUtils.mjs'],
        'mockServerExamples'    : [ 'js',     '{}MockServerExamples.mjs' ],
        'mithrilExamples'       : [ 'js',     '{}MithrilExamples.mjs' ],
        'mithrilConnectors'     : [ 'js',     '{}MithrilConnectors.mjs'],
        'fastApiRoutes'         : [ 'python', '{}FastApiRoutes.py'],
        'fastApiExamples'       : [ 'python', '{}FastApiExamples.py'],
        'natsSubjects'          : [ 'python', '{}NatsSubjects.py']
      },
    }
  }
  try :
    yamlFile = open(configFile)
    yamlConfig = yaml.safe_load(yamlFile.read())
    yamlFile.close()
    cpig.loadInterface.mergeYamlData(config, yamlConfig, "")
  except Exception as ex :
    print("Could not load the configuration file: [{}]".format(configFile))
    print(ex)

  config['options']['verbose'] = verbose
  if 0 < config['options']['verbose'] :
    print("---------------------------------------------------------------")
    print("Configuration:")
    print(yaml.dump(config))
    print("---------------------------------------------------------------")

  return config

@click.command()
@click.option("-c", "--config", 'configFile',
  default="cpigConfig.yaml", show_default=True,
  help="Path to the cpig configuration file.")
@click.option("-v", "--verbose", count=True,
  help="Provide more detail.")
@click.argument('interface_name')
@click.pass_context
def cli(ctx, configFile, verbose, interface_name):
  """
  A simple Python tool to generate computer readable Python and JavaScript
  interfaces from Markdown/YAML descriptions.
  """

  config = loadConfig(configFile, verbose)
  config['outputFiles'] = {}
  config['outputDirs']  = {}

  baseInterfacesDir = os.path.dirname(interface_name)
  if 0 < len(baseInterfacesDir) :
    os.chdir(baseInterfacesDir)
  interface_name = os.path.basename(interface_name)

  cpig.loadInterface.loadInterfaceFile(interface_name)

  cpig.generateCode.computeOutputFileNames(
    config,
    cpig.loadInterface.interfaceDescription
  )
  #print(yaml.dump(config['outputFiles']))
  #print(yaml.dump(config['outputDirs']))

  cpig.generateCode.pydantic(
    config,
    cpig.loadInterface.interfaceDescription
  )

  cpig.generateCode.runSchemaTemplates(
    config,
    cpig.loadInterface.interfaceDescription
  )

  # We run the httpRoutes first as the examples my need to import/require
  # these files.

  cpig.generateCode.runHttpRouteTemplates(
    config,
    cpig.loadInterface.interfaceDescription
  )

  cpig.generateCode.runNatsSubjectsTemplates(
    config,
    cpig.loadInterface.interfaceDescription
  )

  cpig.generateCode.runExampleTemplates(
    config,
    cpig.loadInterface.interfaceDescription
  )

  #print("----------------------------------------")
  #print(yaml.dump(config['options']))
  with open(
    os.path.join(config['options']['distDir'], '__init__.py'),
    "w"
  ) as initFile :
    initFile.write("# This file makes this directory a Python package\n\n")