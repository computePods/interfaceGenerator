
# For file inclusion consider:
#   https://github.com/jreese/markdown-pp

import sys
import yaml

jsonSchemaKeywords = {
  # See: http://json-schema.org/draft/2020-12/json-schema-core.html#vocabulary
  # see: http://json-schema.org/draft/2020-12/json-schema-core.html#id-keyword
  # preamble keywords:
  "_$id_" : True,  
  "_$schema_" : True, 
  "_$vocabulary_" : True,

  # See: http://json-schema.org/draft/2020-12/json-schema-core.html#rfc.section.7.7
  # See: http://json-schema.org/draft/2020-12/json-schema-validation.html#rfc.section.9
  # annotation keywords:
  "_title_" : True,
  "_description_" : True,
  "_deprecated_": True,
  "_readOnly_": True,
  "_writeOnly_": True,
  "_examples_": True,

  # See: http://json-schema.org/draft/2020-12/json-schema-core.html#rfc.section.7.6
  # See: http://json-schema.org/draft/2020-12/json-schema-validation.html#rfc.section.6
  # assertion keywords:
  "_type_" : True,
  "_enum_" : True,
  "_const_" : True,
  "_multipleOf_" : True,
  "_maximum_" : True, 
  "_exclusiveMaximum_" : True,
  "_minimum_" : True,
  "_exclusiveMinimum_" : True,
  "_maxLength_" : True,
  "_minLength_" : True, 
  "_pattern_" : True,
  "_maxItems_" : True,
  "_minItems_" : True,
  "_uniqueItems_" : True,
  "_maxContains_" : True,
  "_minContains_" : True, 
  "_maxProperties_" : True,
  "_minProperties_" : True,
  "_required_" : True,
  "_dependentRequired_" : True, 

  # See: http://json-schema.org/draft/2020-12/json-schema-core.html#rfc.section.7.5
  # See: http://json-schema.org/draft/2020-12/json-schema-validation.html#rfc.appendix.A
  #applicator keywords:
  "_$ref_" : True,
}

def normalizeAJsonType(fieldName, aJsonType) :
  #print("working on the [{}] field".format(fieldName))
  if type(aJsonType) is not dict :
    if fieldName in jsonSchemaKeywords :
      return aJsonType
      
    if type(aJsonType) is not str :
      print("JsonType definitions MUST be a JSON schema keyword, a dictionary or a string")
      return None
    return {
      '_type_' : aJsonType
    }

  if '_dictionary_' in aJsonType :
    additionalFields = {}
    for aKey, aValue in aJsonType.items() :
      if aKey in jsonSchemaKeywords :
        additionalFields[aKey] = aJsonType[aKey]
        
    for aKey in additionalFields :
      del aJsonType[aKey]

    if len(aJsonType) != 1 :
      print("Abbreviated _dictionary_ definitions must consist of ONE key/value")
      return None
    dictDef = {
      '_type_' : 'dictionary',
      '_keys_' : 'string',
      '_items_' : normalizeAJsonType(fieldName+'_dictionary_', aJsonType['_dictionary_'])
    }
    for aField, aValue in additionalFields.items() :
      dictDef[aField] = aValue
    return dictDef

  if '_array_' in aJsonType :
    additionalFields = {}
    for aKey, aValue in aJsonType.items() :
      if aKey in jsonSchemaKeywords :
        additionalFields[aKey] = aJsonType[aKey]

    for aKey in additionalFields :
      del aJsonType[aKey]

    if len(aJsonType) != 1 :
      print("Abbreviated __array__ definitions must consist of ONE key/value")
      return None
    arrayDef = {
      '_type_' : 'array',
      '_items_' : normalizeAJsonType(fieldName+'_array_', aJsonType['_array_'])
    }
    for aField, aValue in additionalFields.items() :
      arrayDef[aField] = aValue
    return arrayDef

  # deal with the real type delcarations
  #
  realType = False
  newJsonType = {}
  if '_type_' in aJsonType :
    realType = True
    newJsonType['_type_'] = normalizeAJsonType(aJsonType['_type_'])
    del aJsonType['_type_']
  if '_items_' in aJsonType :
    realType = True
    newJsonType['_items_'] = normalizeAJsonType(aJsonType['_items_'])
    del aJsonType['_items_']
  if '_default_' in aJsonType :
    realType = True
    newJsonType['_default_'] = aJsonType['_default_']
    del aJsonType['_default_']
  if '_keys_' in aJsonType :
    realType = True
    newJsonType['_keys_'] = 'string'
    del aJsonType['_keys_']

  # Now deal with a possibly abbreviated type definition
  #
  if realType and 0 < len(aJsonType) :
    print("You can NOT mix real and abbreviated type definitions")
    return None
  if realType : 
    return newJsonType

  objectFields = {}
  additionalFields = {}
  for subFieldName, subFieldDefinition in aJsonType.items() :
    if subFieldName in jsonSchemaKeywords :
      additionalFields[subFieldName] = subFieldDefinition
      continue
      
    objectFields[subFieldName] = normalizeAJsonType(fieldName+'.'+subFieldName, subFieldDefinition)

  objDef = {
      '_type_' : 'object',
      '_properties_' : objectFields,
    }
  for aField, aValue in additionalFields.items() :
    objDef[aField] = aValue
  return  objDef
  
def normalizeJsonTypes(someJsonTypes) :
  if type(someJsonTypes) is not dict :
    print("JsonTypes MUST be a dictionary")
    return None
  if len(someJsonTypes) < 1 :
    print("JsonTypes MUST contain at least one field")
    return None

  for jsonTypesKey, jsonTypesValue in someJsonTypes.items() :

    if type(jsonTypesValue) is not dict :
      print("JsonTypes MUST contain a dictionary")
      return None
    
    for fieldName, fieldDefinition in jsonTypesValue.items() :
      jsonTypesValue[fieldName] = normalizeAJsonType(fieldName, fieldDefinition)
    
  return someJsonTypes

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

def exportJsonSchema(jsonTypes) :
  jsonSchema = {}
  for aKey, aValue in jsonTypes.items() :
    jsonSchema[aKey.strip('_')] = aValue
  return jsonSchema

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
  if 'jsonTypes' in newYamlData[0] :
    newYamlData = normalizeJsonTypes(newYamlData[0])
  elif 'jsonExamples' in newYamlData[0] :
    newYamlData = normalizeJsonExample(newYamlData)
  elif 'httpRoutes' in newYamlData[0] :
    newYamlData = newYamlData[0]
  elif 'natsChannels' in newYamlData :
    newYamlData = newYamlData[0]
  else :
    print("The YAML block must contain a 'jsonTypes', 'jsonExamples', 'httpRoutes' or 'natsChannel' definition.")
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

def loadInterfaceFile(interfaceFileName) :
  print("Working on {}".format(interfaceFileName))
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
