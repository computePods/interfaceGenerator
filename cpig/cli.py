
# For file inclusion consider:
#   https://github.com/jreese/markdown-pp

import click
import copy
import cpig.loadInterface
import cpig.generateCode
import datamodel_code_generator
import json
import yaml

def loadConfig(configFile, verbose) :
  config = {
    'pythonOutput' : 'dist/python',
    'jsOutput'     : 'dist/js',
  }
  try :
    yamlFile = open(configFile)
    yamlConfig = yaml.safe_load(yamlFile.read())
    yamlFile.close()
    if type(yamlConfig) is dict :
      config.update(yamlConfig)
    elif type(yamlConfig) is list :
      for aKey in yamlConfig :
        config[aKey] = True
    elif type(yamlConfig) is str :
      config[yamlConfig] = True
  except Exception as ex :
    print("Could not load the configuration file: [{}]".format(configFile))
    print(ex)

  config['verbose'] = verbose
  if 0 < config['verbose'] :
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

  cpig.loadInterface.loadInterfaceFile(interface_name)

  cpig.generateCode.pydantic(
    config,
    cpig.loadInterface.interfaceDescription    
  )

  cpig.generateCode.ajv(
    config,
    cpig.loadInterface.interfaceDescription    
  )
