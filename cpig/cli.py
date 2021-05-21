
# For file inclusion consider:
#   https://github.com/jreese/markdown-pp

import click
import cpig.loadInterface
import sys
import yaml

def loadConfig(configFile) :
  config = { }
  try :
    yamlFile = open(configFile)
    yamlConfig = yaml.safe_load(yamlFile.read())
    yamlFile.close()
    config.update(yamlConfig)
  except :
    print("Could not load the configuration file: [{}]".format(configFile))
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

  config = loadConfig(configFile)

  if 0 < verbose :
    print("---------------------------------------------------------------")
    print("Configuration:")
    print(yaml.dump(config))
    print("---------------------------------------------------------------")

  cpig.loadInterface.loadInterfaceFile(interface_name)

  print("---------------------------------------------------------")
  print(yaml.dump(cpig.loadInterface.interfaceDescription))
  print("---------------------------------------------------------")

  jsonSchema = cpig.loadInterface.exportJsonSchema(
    cpig.loadInterface.interfaceDescription    
  )
  print("---------------------------------------------------------")
  print(yaml.dump(jsonSchema))
  print("---------------------------------------------------------")
