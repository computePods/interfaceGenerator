
# For file inclusion consider:
#   https://github.com/jreese/markdown-pp

import copy
import datamodel_code_generator
import json
import os
import pathlib
import yaml


def jsonSchemaGenerator(interfaceDefinition) :

  if 'jsonSchemaPreambles' not in interfaceDefinition :
    return [None, {}]
  preambles = interfaceDefinition['jsonSchemaPreambles']
  
  if 'jsonSchemaDefs' not in interfaceDefinition :
    return [None, {}]
  defs = interfaceDefinition['jsonSchemaDefs']
  
  for aRootType, somePreamble in preambles.items() :
    if aRootType not in defs :
      continue
      
    jsonSchema = {}
    for aKey, aValue in somePreamble.items() :
      jsonSchema[aKey] = copy.deepcopy(aValue)

    if 'title' not in jsonSchema :
      jsonSchema['title'] = aRootType

    for aKey, aValue in defs[aRootType].items() :
      jsonSchema[aKey] = copy.deepcopy(aValue)

    theDefs = {}
    if 'jsonSchemaDefs' in interfaceDefinition :
      for aKey, aValue in interfaceDefinition['jsonSchemaDefs'].items() :
        theDefs[aKey] = copy.deepcopy(aValue)

    jsonSchema['$defs'] = theDefs

    yield [aRootType, jsonSchema]

def pydantic(config, interfaceDefinition) :
  if 'pydantic' not in config :
    return

  for aRootType, aJsonSchema in jsonSchemaGenerator(interfaceDefinition) :
    outputPath = os.path.join(config['pythonOutput'], aRootType+'.py')
    os.makedirs(config['pythonOutput'], exist_ok=True)
    print("Generating pydantic {} to {}".format(aRootType, outputPath))
    print("---------------------------------------------------------")
    try: 
      datamodel_code_generator.generate(
        json.dumps(aJsonSchema),
        output=pathlib.Path(outputPath),
      )
    except Exception as ex :
      print("Error found while parsing the [{}] JSON type".format(aRootType))
      print("  "+"\n    ".join(str(ex).split("\n")))
      print("(It may have been inside a reference to another type)")


def ajv(config, interfaceDefinition) :
  if 'ajv' not in config :
    return

  for aRootType, aJsonSchema in jsonSchemaGenerator(interfaceDefinition) :
    outputPath = os.path.join(config['jsOutput'], aRootType+'.py')
    os.makedirs(config['jsOutput'], exist_ok=True)
    print("Generating ajv {} to {}".format(aRootType, outputPath))
    print("---------------------------------------------------------")
  
"""
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

"""