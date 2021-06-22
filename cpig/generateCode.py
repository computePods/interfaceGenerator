
# For file inclusion consider:
#   https://github.com/jreese/markdown-pp

import copy
import datamodel_code_generator
import importlib.resources
import jinja2
import json
import os
import pathlib
import yaml

def loadTemplate(options, generationType, generationDetails) :
  jinjaTemplatePath = None
  if 'jinja2' in generationDetails :
    jinjaTemplatePath = generationDetails['jinja2']
    del generationDetails['jinja2']

  theTemplateStr = None
  if jinjaTemplatePath and os.path.exists(jinjaTemplatePath) :
    with open(jinjaTemplatePath, 'r') as jinjaFile :
      theTemplateStr = jinjaFile.read()
  else :
    generationFileName = generationType + '.j2'
    if importlib.resources.is_resource('cpig.templates', generationFileName) :
      theTemplateStr = importlib.resources.read_text('cpig.templates', generationFileName)
      jinjaTemplatePath = 'cpig/'+generationFileName

  if not theTemplateStr :
    print("No jinja2 template found for {} [{}]".format(generationType, jinjaTemplatePath))
    return [ None, jinjaTemplatePath ]

  try :
    theTemplate = jinja2.Template(theTemplateStr)
  except Exception as ex :
    print("Could not create the Jinja2 template [{}]".format(jinjaTemplatePath))
    print(ex)
    return [ None, jinjaTemplatePath ]

  return [ theTemplate, jinjaTemplatePath ]

def getOutputPaths(options, generationType, generationDetails) :
  distDir = options['distDir']

  if 'outputPathTemplate' not in generationDetails :
    outputPathTemplates = options['outputPathTemplates']
    if generationType not in outputPathTemplates :
      print("Could not determine the output path template for the {} code generator".format(generationType))
      return [ None, None ]
    else:
      outputPathTemplate = outputPathTemplates[generationType]
  else:
    outputPathTemplate = generationDetails['outputPathTemaplate']

  outputPathTemplate.insert(0, distDir)
  outputPathTemplate = os.path.join(*outputPathTemplate)
  outputDir = os.path.dirname(outputPathTemplate)

  return [ outputDir, outputPathTemplate ]

def jsonSchemaGenerator(options, interfaceDefinition) :
  if 1 < options['verbose'] :
    print("Generating json schema for {}".format(interfaceDefinition['name']))

  preambles = { }
  if 'jsonSchemaPreambles' in interfaceDefinition :
    preambles = interfaceDefinition['jsonSchemaPreambles']

  if 'jsonSchemaDefs' not in interfaceDefinition :
    if 1 < options['verbose'] :
      print("NO jsonSchemaDefs found in {}".format(interfaceName))
    return [None, {}]
  defs = interfaceDefinition['jsonSchemaDefs']

  rootTypes = {}
  if 'httpRoutes' in interfaceDefinition :
    httpRoutes = interfaceDefinition['httpRoutes']
    for  aRouteKey, aRoute in httpRoutes.items() :
      if 'response' in aRoute :
        rootTypes[aRoute['response']] = True

  if 2 < options['verbose'] :
    print("rootTypes:")
    print(yaml.dump(rootTypes))

  for aRootType in rootTypes :
    if aRootType not in defs :
      continue

    somePreamble = {}
    if aRootType in preambles :
      somePreamble.update(preambles[aRootType])

    jsonSchema = {}
    for aKey, aValue in somePreamble.items() :
      jsonSchema[aKey] = copy.deepcopy(aValue)

    if 'title' not in jsonSchema :
      jsonSchema['title'] = aRootType

    for aKey, aValue in defs[aRootType].items() :
      jsonSchema[aKey] = copy.deepcopy(aValue)

    theDefs = {}
    for aKey, aValue in defs.items() :
      theDefs[aKey] = copy.deepcopy(aValue)

    jsonSchema['$defs'] = theDefs

    if 2 < options['verbose'] :
      print("Yielding {} with schema \n{}".format(aRootType, yaml.dump(jsonSchema)))
    yield [aRootType, jsonSchema]

def pydantic(config, interfaceDefinition) :
  interfaceName = interfaceDefinition['name']
  options = config['options']
  if 'genSchema' not in config :
    return

  if 'pydantic' not in config['genSchema'] :
    return

  if 1 < options['verbose'] :
    print("Running pydantic schema templates on {}".format(interfaceName))

  outputDir, outputPathTemplate = getOutputPaths(
    config['options'], 'pydantic', config['genSchema']['pydantic'])
  if outputDir is None :
    return

  for aRootType, aJsonSchema in jsonSchemaGenerator(options, interfaceDefinition) :
    outputPath = outputPathTemplate.format(aRootType)
    config['outputFiles'][aRootType+'-rootType-py'] = os.path.basename(outputPath)
    os.makedirs(outputDir, exist_ok=True)
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
      print("---------------------------------------------------------------")
      print(yaml.dump(aJsonSchema))
      print("---------------------------------------------------------------")

def runSchemaTemplates(config, interfaceDefinition) :
  interfaceName = interfaceDefinition['name']
  if 1 < config['options']['verbose'] :
    print("Running schema templates on {}".format(interfaceName))
  #
  # setup the collection of generators for our use...
  #
  generatorOptions = copy.deepcopy(config)
  options = generatorOptions['options']
  if 'genSchema' not in generatorOptions :
    return
  generatorOptions = generatorOptions['genSchema']
  del generatorOptions['pydantic']

  for generationType, generationDetails in generatorOptions.items() :
    if 1 < config['options']['verbose'] :
      print("Running {} schema templates on {}".format(generationType, interfaceName))

    theTemplate, jinjaTemplatePath = loadTemplate(
      options, generationType, generationDetails)
    if theTemplate is None :
      continue

    outputDir, outputPathTemplate = getOutputPaths(
      options, generationType, generationDetails)
    if outputDir is None :
      continue

    for aRootType, aJsonSchema in jsonSchemaGenerator(options, interfaceDefinition) :
      outputPath = outputPathTemplate.format(aRootType)
      config['outputFiles'][aRootType+'-rootType-js'] = os.path.basename(outputPath)
      os.makedirs(outputDir, exist_ok=True)
      print("Generating {} {} to {}".format(generationType, aRootType, outputPath))
      print("---------------------------------------------------------")

      generationDetails['interfaceName'] = interfaceName
      generationDetails['rootType'] = aRootType
      try :
        renderedStr = theTemplate.render({
          'options'     : generationDetails,
          'outputFiles' : config['outputFiles'],
          'schema'      : aJsonSchema,
        })
        with open(outputPath, 'w') as outFile :
          outFile.write(renderedStr)
      except Exception as ex :
        print("Could not render the Jinja2 template [{}] using the {} JSON Schema".format(jinjaTemplatePath, aRootType ))
        print(ex)

spaceTranslator = str.maketrans(' ', '_')

def runExampleTemplates(config, interfaceDefinition) :

  interfaceName = interfaceDefinition['name']

  if 'jsonExamples' not in interfaceDefinition :
    return

  jsonExamples = interfaceDefinition['jsonExamples']
  #
  # setup the collection of generators for our use...
  #
  generatorOptions = copy.deepcopy(config)
  options = generatorOptions['options']
  if 'genExamples' not in generatorOptions :
    return
  generatorOptions = generatorOptions['genExamples']

  for generationType, generationDetails in generatorOptions.items() :

    theTemplate, jinjaTemplatePath = loadTemplate(
      options, generationType, generationDetails)

    outputDir, outputPathTemplate = getOutputPaths(
      options, generationType, generationDetails)
    if outputDir is None :
      continue

    outputPath = outputPathTemplate.format(interfaceName)
    config['outputFiles'][generationType+'-examples'] = os.path.basename(outputPath)
    os.makedirs(outputDir, exist_ok=True)
    print("Generating {} {} to {}".format(generationType, interfaceName, outputPath))
    print("---------------------------------------------------------")

    for exampleType, exampleDetails in jsonExamples.items() :
      exampleNum = 0
      for anExample in exampleDetails :
        exampleNum += 1
        if 'title' in anExample :
          anExample['name'] = anExample['title'].translate(spaceTranslator)
        else :
          anExample['name'] = "{}_{}".format(interfaceName, exampleNum)

    generationDetails['interfaceName'] = interfaceName
    try :
      renderedStr = theTemplate.render({
        'options'     : generationDetails,
        'outputFiles' : config['outputFiles'],
        'examples'    : jsonExamples,
      })
      with open(outputPath, 'w') as outFile :
        outFile.write(renderedStr)
    except Exception as ex :
      print("Could not render the Jinja2 template [{}] using the {} jsonExamples".format(jinjaTemplatePath, interfaceName ))
      print(ex)

def runHttpRouteTemplates(config, interfaceDefinition) :
  interfaceName = interfaceDefinition['name']

  if 'httpRoutes' not in interfaceDefinition :
    return
  httpRoutes = interfaceDefinition['httpRoutes']

  if 'jsonSchemaDefs' not in interfaceDefinition :
    return
  jsonSchemaDefs = interfaceDefinition['jsonSchemaDefs']

  #
  # setup the collection of generators for our use...
  #
  generatorOptions = copy.deepcopy(config)
  options = generatorOptions['options']
  if 'genHttpRoutes' not in generatorOptions :
    return
  generatorOptions = generatorOptions['genHttpRoutes']

  for generationType, generationDetails in generatorOptions.items() :

    theTemplate, jinjaTemplatePath = loadTemplate(
      options, generationType, generationDetails)

    outputDir, outputPathTemplate = getOutputPaths(
      options, generationType, generationDetails)
    if outputDir is None :
      continue

    outputPath = outputPathTemplate.format(interfaceName)
    config['outputFiles'][generationType+'-httproutes'] = os.path.basename(outputPath)
    os.makedirs(outputDir, exist_ok=True)
    print("Generating {} {} to {}".format(generationType, interfaceName, outputPath))
    print("---------------------------------------------------------")

    rootTypeFiles = {}
    for anOutputKey, anOutputFile in config['outputFiles'].items() :
      if anOutputKey.endswith('-rootType-js') :
        rootTypeFiles[anOutputKey.split('-')[0]] = anOutputFile

    generationDetails['interfaceName'] = interfaceName
    try :
      #print(yaml.dump(config['outputFiles']))
      #print(yaml.dump(rootTypeFiles))
      renderedStr = theTemplate.render({
        'options'        : generationDetails,
        'outputFiles'    : config['outputFiles'],
        'rootTypeFiles'  : rootTypeFiles,
        'httpRoutes'     : httpRoutes,
        'jsonSchemaDefs' : jsonSchemaDefs,
      })
      with open(outputPath, 'w') as outFile :
        outFile.write(renderedStr)
    except Exception as ex :
      print("Could not render the Jinja2 template [{}] using the {} httpRoutes".format(jinjaTemplatePath, interfaceName ))
      print(ex)
