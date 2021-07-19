import copy
import json
import jsonschema
import os
import re
import sys
import yaml

# We validate the following schema using: jsonschema.Draft7Validator
# see: https://stackoverflow.com/a/13826826
#
interfaceSchemasYaml = """
  jsonSchemaPreamble:
    # is a dictionary of jsonType -> JSON Schema preamble strings
    type: dictionary
    items:
      type: dictionary
      items:
        type: string

  jsonSchemaDefs:
    # is a dictionary of jsonType -> JSON Schema definitions
    type: dictionary
    items:
      type: draft7  # A (draft 7) JSON Schema

  jsonExamplesHeader:
    # is a dictionary of jsonType -> HTTP route fragments
    type: object
    properties:
      title:
        type: string
      httpRoutes:
        type: object
        properties:
          # an httpRoute fragment is a object of:
          #  - an example route (URL)
          #  - an action
          route:
            type: string
          action:
            enum:
             - GET
             - POST
             - PUT
             - DELETE

  httpRoutes:
    # is a dictionary of mountPoints -> httpRoutes
    type: dictionary
    items:
      # an httpRoute is a dictionary of:
      #  - a list of actions (GET, POST, PUT, DELETE)
      #  - a declaration of the request/response body format
      #    as a jsonType in the jsonSchemaDefs
      #  - the URL template (which may include <name> elements)
      #
      # We follow a RESTful interface guide lines:
      # See: https://en.wikipedia.org/wiki/Representational_state_transfer#Semantics_of_HTTP_methods
      #
      type: object
      properties:
        body:
          # the name of a jsonType in the jsonSchemaDefs
          type: string
        url:
          # the URL template for this mount point
          type: string
        actions:
          type: array
          items:
            enum:
              - GET
              - POST
              - PUT
              - DELETE

  natsSubjects: { }
    # is a dictionary of NATS subjects -> ????
"""

def validateJsonData(jsonData, aSchemaName) :
  if aSchemaName not in interfaceSchemas :
    print("Interface schema name {} has not been defined".format(aSchemaName))
    print(yaml.dump(jsonData))
    return

  if aSchemaName == 'jsonSchemaDefs' :
    validateSchema(aSchemaName, jsonData)
    return

  aSchema = interfaceSchemas[aSchemaName]
  try :
    jsonschema.validate(
      instance=jsonData,
      schema=aSchema,
    )
  except Exception as ex :
    print("Could not validate the schema {}".format(aSchemaName))
    print("--------------------------------------------------------")
    print(yaml.dump(jsonData))
    print("--------------------------------------------------------")
    print(yaml.dump(aSchema))
    print("--------------------------------------------------------")
    print(ex)
    sys.exit(-1)

def validateSchema(aSchemaName, aSchema) :
  try :
    jsonschema.Draft7Validator.check_schema(aSchema)
  except Exception as ex :
    print("Could not validate the schema {}".format(aSchemaName))
    print("--------------------------------------------------------")
    print(yaml.dump(aSchema))
    print("--------------------------------------------------------")
    print(ex)
    sys.exit(-1)

def normalizeJsonSchema(aJsonSchema) :
  #
  # We translate our version of 'dictionaries' to the official JSON schema
  # version as suggested by:
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

def normalizeHttpRoutes(someHttpRoutes) :
  #
  # We expand the route into its constituent parts
  #
  if type(someHttpRoutes) is not dict :
    return

  if 'httpRoutes' not in someHttpRoutes :
    return
  httpRoutes = someHttpRoutes['httpRoutes']

  for mountPointName, mpDetails in someHttpRoutes['httpRoutes'].items() :
    if 'route' in mpDetails :
      routeDirs = mpDetails['route'].split('/')
      mountPoint = ""
      routeParts = []
      i = 0
      while i < len(routeDirs) and not routeDirs[i].startswith('<') :
        if routeDirs[i] != '' :
          mountPoint = mountPoint+'/'+routeDirs[i]
        i = i + 1
      while i < len(routeDirs) :
        routeParts.append(routeDirs[i].strip('<>'))
        i = i + 1
      mpDetails['mountPoint'] = mountPoint
      mpDetails['routeParts'] = routeParts

def normalizeNatsSubjects(someNatsSubjects) :
  #
  # We expand the subject into its constituent parts
  #
  if type(someNatsSubjects) is not dict :
    return

  if 'natsSubjects' not in someNatsSubjects :
    return
  natsSubjects = someNatsSubjects['natsSubjects']
  print("===============================================+++")
  print(yaml.dump(natsSubjects))
  print("===============================================+++")
  for subjectName, subjectDetails in someNatsSubjects['natsSubjects'].items() :
    if 'subject' in subjectDetails :
      subjectFields = subjectDetails['subject'].split('.')
      baseSubject = ""
      subjectParts = []
      subjectWildcards = {}
      i = 0
      while i < len(subjectFields) and not subjectFields[i].startswith( ('<', '[') ) :
        if subjectFields[i] != '' :
          baseSubject = baseSubject+'.'+subjectFields[i]
        i = i + 1
      while i < len(subjectFields) :
        if subjectFields[i].startswith('[') :
          subjectWildcards[subjectFields[i].strip('<[]>')] = ('>')
        else :
          subjectWildcards[subjectFields[i].strip('<[]>')] = ('*')
        subjectParts.append(subjectFields[i].strip('<[]>'))
        i = i + 1
      subjectDetails['baseSubject']      = baseSubject.strip('.')
      subjectDetails['subjectParts']     = subjectParts
      subjectDetails['subjectWildcards'] = subjectWildcards

def loadInterfaceSchemas() :
  global interfaceSchemas
  if interfaceSchemas is None :
    interfaceSchemas = yaml.safe_load(interfaceSchemasYaml)
    normalizeJsonSchema(interfaceSchemas)
    for aSchemaName, aSchema in interfaceSchemas.items() :
      if aSchemaName != 'jsonSchemaDefs' :
        validateSchema(aSchemaName, aSchema)

interfaceSchemas = None
loadInterfaceSchemas()

def normalizeJsonExample(newYamlData) :
  # we have found a jsonExample which we need to deal with
  #
  # jsonExamples consist of two YAML documents...
  #   the first document describes the example:
  #     - which jsonType it corresponds to
  #     - and an interface it will be used with
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
      print("JsonExamples MUST have the 'jsonExamples' key")
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
      elif 'natsSubjects' in exampleValue :
        pass
      else :
        print("The example in a jsonExamples MUST have either an httpRoutes or natsSubject")
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
  # This is a generic Python merge
  # It is a *deep* merge and handles both dictionaries and arrays
  #
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
  if not newYamlData :
    return # there is no YAML data (that we could parse) in this block
  # Check and normalise the loaded YAML data
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
    validateJsonData(newYamlData, 'jsonSchemaDefs')
  elif 'jsonExamples' in newYamlData[0] :
    validateJsonData(newYamlData[0], 'jsonExamplesHeader')
    newYamlData = normalizeJsonExample(newYamlData)
  elif 'httpRoutes' in newYamlData[0] :
    newYamlData = newYamlData[0]
    validateJsonData(newYamlData, 'httpRoutes')
    normalizeHttpRoutes(newYamlData)
  elif 'natsSubjects' in newYamlData[0] :
    newYamlData = newYamlData[0]
    normalizeNatsSubjects(newYamlData)
    validateJsonData(newYamlData, 'natsSubjects')
  elif 'jsonSchemaPreambles' in newYamlData[0] :
    newYamlData = newYamlData[0]
    validateJsonData(newYamlData, 'jsonSchemaPreambles')
  else :
    print("The YAML block must contain a 'jsonSchemaPreambles', 'jsonSchemaDefs', 'jsonExamples', 'httpRoutes' or 'natsSubjects' definition.")
    print("--------------------------------------------------------------")
    print("\n  ".join(yamlLines))
    print("--------------------------------------------------------------")
    return

  # Check and merge the normalised YAML data
  #
  if newYamlData is None :
    return # the normalisation failed....
  #
  mergeYamlData(interfaceDescription, newYamlData, "")


def checkEntityInterfaceMapping() :
  # The over all interface MUST have an entityInterfaceMapping
  #
  # AND all of the mount points MUST have been defined
  #
  # AND all of the entityTypes MUST have been defined in the entityType
  #     definition

  if 'jsonExamples' not in interfaceDescription :
    print("Error no entityInterfaceMapping found (no jsonExamples)")
    print(yaml.dump(interfaceDescription))
    sys.exit(-1)
  jsonExamples = interfaceDescription['jsonExamples']

  if 'entityInterfaceMapping' not in jsonExamples :
    print("Error no entityInterfaceMapping found")
    print(yaml.dump(jsonExamples))
    sys.exit(-1)
  entityInterfaceMapping = jsonExamples['entityInterfaceMapping'][0]

  if 'example' not in entityInterfaceMapping :
    print("Error no entityInterfaceMapping found (no details)")
    print(yaml.dump(entityInterfaceMapping))
    sys.exit(-1)

  if 'httpRoutes' not in interfaceDescription :
    print("Error no httpRoutes defined for entityInterfaceMapping")
    print(yaml.dump(interfaceDescription))
    sys.exit(-1)
  httpRoutes = interfaceDescription['httpRoutes']

  if 'jsonSchemaDefs' not in interfaceDescription :
    print("Error no jsonSchemaDefs defined for entityInterfaceMapping")
    print(yaml.dump(interfaceDescription))
    sys.exit(-1)
  jsonSchemaDefs = interfaceDescription['jsonSchemaDefs']

  if 'entityType' not in jsonSchemaDefs :
    print("Error no entityType defined in jsonSchemaDefs")
    print(yaml.dump(jsonSchemaDefs))
    sys.exit(-1)
  entityTypeDef = jsonSchemaDefs['entityType']

  if (
    'properties' not in entityTypeDef or
    'entityType' not in entityTypeDef['properties'] or
    'enum' not in entityTypeDef['properties']['entityType']
    ) :
    print("Error no entityType enumeration in entityType definition")
    print(yaml.dump(entityTypeDef))
    sys.exit(-1)
  entityTypeEnum = entityTypeDef['properties']['entityType']['enum']

  entityInterfaceMapping = entityInterfaceMapping['example']
  for entityType, mountPoint in entityInterfaceMapping.items() :
    if mountPoint not in httpRoutes :
      print("Error: missing mountPoint [{}] for the entityType [{}]".format(mountPoint, entityType))
      print("--------------------------------------------------------------------")
      print(yaml.dump(entityInterfaceMapping))
      print("--------------------------------------------------------------------")
      print(yaml.dump(httpRoutes))
      print("--------------------------------------------------------------------")
      sys.exit(-1)
    if entityType not in entityTypeEnum :
      print("Error: missing entityType [{}] in entityType definition".format(entityType))
      print("--------------------------------------------------------------------")
      print(yaml.dump(entityInterfaceMapping))
      print("--------------------------------------------------------------------")
      print(yaml.dump(entityTypeDef))
      print("--------------------------------------------------------------------")
      sys.exit(-1)

def checkInterfaceDescription() :
  checkEntityInterfaceMapping()

sepTranslator = str.maketrans('/\\', '__')
includeInterfaceMatcher = re.compile(r"Include\.Interface\:\s\[.+\]\((.+)\)")

def loadInterfaceFile(interfaceFileName) :
  print("Working on {}".format(interfaceFileName))

  shouldCheckInterfaceDescription = False
  if 'name' not in interfaceDescription :
    # the name of the first interface file loaded... wins...
    baseName, extension = os.path.splitext(interfaceFileName)
    interfaceDescription['name'] = baseName.translate(sepTranslator)
    shouldCheckInterfaceDescription = True

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
      includeMatch = includeInterfaceMatcher.search(line)
      if includeMatch :
        loadInterfaceFile(includeMatch.group(1))
      elif line != "```yaml" :
        pass
      else :
        insideYaml = True

  if shouldCheckInterfaceDescription :
    checkInterfaceDescription()
