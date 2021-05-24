
# For file inclusion consider:
#   https://github.com/jreese/markdown-pp

import copy
import os
import sys
import yaml

def normalizeJsonSchema(aJsonSchema) :
  #
  # We translate our version of 'dictionaries' to the official JSON schema 
  # versino as suggested by:
  #
  # https://stackoverflow.com/questions/27357861/dictionary-like-json-schema
  #
  if type(aJsonSchema) is not dict :
    return

  if 'type' in aJsonSchema :
    if aJsonSchema['type'] == "dictionary" :
      aJsonSchema['type'] = "object"
      if 'items' in aJsonSchema :
        aJsonSchema['additionalProperties'] = aJsonSchema['items']
        del aJsonSchema['items']

  for aKey, aValue in aJsonSchema.items() :
    normalizeJsonSchema(aValue)

def normalizeJsonExample(newYamlData) :
  # we have found a jsonExample which we need to deal with
  #
  # jsonExamples consist of two YAML documents...
  #   the first document describes the example
  #     which jsonType it corresponds to
  #     and an interface it will be used with
  #   the second document is the message itself
  if len(newYamlData) < 2 :
    print("jsonExamples MUST consist of TWO YAML documents... only one found")
    return None

  exampleHeader = newYamlData[0]
  exampleBody   = newYamlData[1]
  if type(exampleHeader) is not dict :
    print("JsonExamples MUST be dictionaries")
    return None
  if 1 < len(exampleHeader) :
    print("JsonExamples MUST only contain ONE key/value pair")
    return None
  for jsonExampleKey, jsonExampleValue in exampleHeader.items() :
    if jsonExampleKey != 'jsonExamples' :
      print("JsonExamples MUST have the 'jsonExamles' key")
      return None
    if type(jsonExampleValue) is not dict :
      print("The example in a JsonExamples MUST be a dictionary")
      return None
    if 1 < len(jsonExampleValue) :
      print("The example in a jsonExamples MUST have ONE key/value")
      return None
    for exampleKey, exampleValue in jsonExampleValue.items() :
      if type(exampleValue) is not dict :
        print("The example in a jsonExamples must be a dictionary")
        return None
      if 'title' not in exampleValue :
        print("The example in a jsonExamples MUST have a title")
        return None
      if 'httpRoutes' in exampleValue :
        pass
      elif 'natsChannels' in exampleValue :
        pass
      else :
        print("The example in a jsonExamples MUST have either an httpRoutes or natsChannel")
        return None
      exampleValue['example'] = exampleBody
      return { 'jsonExamples':
        {
          exampleKey : [ exampleValue ]
        }
      }
      
  print("ERROR we should not have got here!")
  return None

def mergeYamlData(yamlData, newYamlData, thePath) :
  if type(yamlData) is None :
    print("ERROR yamlData should NEVER be None ")
    sys.exit(-1)
    
  if type(yamlData) != type(newYamlData) :
    print("Incompatible types {} and {} while trying to merge YAML data at {}".format(type(yamlData), type(newYamlData), thePath))
    print("Stoping merge at {}".format(thePath))
    return

  if type(yamlData) is dict :
    for key, value in newYamlData.items() :
      if key not in yamlData :
        yamlData[key] = value
      elif type(yamlData[key]) is dict :
        mergeYamlData(yamlData[key], value, thePath+'.'+key)
      elif type(yamlData[key]) is list :
        for aValue in value :
          yamlData[key].append(aValue)
      else :
        yamlData[key] = value
  elif type(yamlData) is list :
    for value in newYamlData :
      yamlData.append(value)
  else :
    print("ERROR yamlData MUST be either a dictionary or an array.")
    sys.exit(-1)

interfaceDescription = {}

def addYamlBlock(yamlLines) :
  newYamlData = None
  try :
    newYamlData = []
    for someYaml in yaml.safe_load_all("\n".join(yamlLines)) :
      newYamlData.append(someYaml)
  except Exception as ex:
    print("Could not parse the YAML code block: ")
    print("--------------------------------------------------------------")
    print("\n  ".join(yamlLines))
    print("--------------------------------------------------------------")
    print("Error: {}".format(ex))
    print("--------------------------------------------------------------")
  if newYamlData is None :
    return # there is no yaml data (that we could parse) in this block

  # Check and normalize the loaded YAML data
  #
  if type(newYamlData[0]) is not dict :
    print("The base of a YAML block MUST be a dictionary")
    return
  if len(newYamlData[0]) != 1 :
    print("The base of a YAML block must contain ONE key/value")
    return
  #
  if 'jsonSchemaDefs' in newYamlData[0] :
    newYamlData = newYamlData[0]
    normalizeJsonSchema(newYamlData)
  elif 'jsonExamples' in newYamlData[0] :
    newYamlData = normalizeJsonExample(newYamlData)
  elif 'httpRoutes' in newYamlData[0] :
    newYamlData = newYamlData[0]
  elif 'natsChannels' in newYamlData :
    newYamlData = newYamlData[0]
  elif 'jsonSchemaPreambles' in newYamlData[0] :
    newYamlData = newYamlData[0]
  else :
    print("The YAML block must contain a 'jsonSchemaPreambles', 'jsonSchemaDefs', 'jsonExamples', 'httpRoutes' or 'natsChannel' definition.")
    print("--------------------------------------------------------------")
    print("\n  ".join(yamlLines))
    print("--------------------------------------------------------------")
    return


  # Check and merge the normalized YAML data
  #
  if newYamlData is None :
    return # the normalization failed....
  #
  mergeYamlData(interfaceDescription, newYamlData, "")

sepTranslator = str.maketrans('/\\', '__')

def loadInterfaceFile(interfaceFileName) :
  print("Working on {}".format(interfaceFileName))

  baseName, extension = os.path.splitext(interfaceFileName)
  interfaceDescription['name'] = baseName.translate(sepTranslator)
  
  interface = open(interfaceFileName)
  lines = interface.readlines()
  interface.close()
  insideYaml = False
  theYaml = []
  for line in lines :
    line = line.rstrip()
    if insideYaml :
      if line != "```" :
        theYaml.append(line)
      else :
        addYamlBlock(theYaml)
        theYaml = []
        insideYaml = False
    else :
      if line != "```yaml" :
        pass
      else :
        insideYaml = True
