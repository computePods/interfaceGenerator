
# For file inclusion consider:
#   https://github.com/jreese/markdown-pp

import click
import copy
import cpig.loadInterface
import datamodel_code_generator
import json
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
  print(json.dumps(jsonSchema))
  print("---------------------------------------------------------")
  for aType, aDef in jsonSchema['$defs'].items() :
    newJsonSchema = copy.deepcopy(jsonSchema)
    for aKey, aValue in aDef.items() :
      newJsonSchema[aKey] = copy.deepcopy(aValue)
      newJsonSchema['title'] = aType
    print(yaml.dump(newJsonSchema))
    print("---------------------------------------------------------")
    print(json.dumps(newJsonSchema, sort_keys=True, indent=2))
    print("---------------------------------------------------------")
    with open('/tmp/silly.py', 'w') as outFile :
      outFile.write("import yaml\n")
      outFile.write("\n")
      outFile.write("test = {}\n".format(json.dumps(newJsonSchema, sort_keys=True, indent=2)))
      outFile.write("\n")
      outFile.write("print(yaml.dump(test))\n")
      outFile.write("\n")

    try: 
      datamodel_code_generator.generate(json.dumps(newJsonSchema))
    except Exception as ex :
      print("Error found while parsing the [{}] JSON type".format(aType))
      print("  "+"\n    ".join(str(ex).split("\n")))
      print("(It may have been inside a reference to another type)")
    print("---------------------------------------------------------")
