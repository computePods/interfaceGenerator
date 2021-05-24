
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
    if options['verbose'] :
      print("No jinja2 template found for {} [{}]".format(generationType, jinjaTemplatePath))
      return [ None, jinjaTemplatePath ]
  try : 
    theTemplate = jinja2.Template(theTemplateStr)
  except Exception as ex :
    print("Could not create the Jinja2 template [{}]".format(jinjaTemplatePath))
    print(ex)

  return [ theTemplate, jinjaTemplatePath ]

def getOutputPaths(options, generationType, generationDetails) :
  distDir = options['distDir']
  
  if 'outputPathTemplate' not in generationDetails :
    outputPathTemplates = options['outputPathTemplates']
    if generationType not in outputPathTemplates :
      print("Could not determine the output path template for the {} code generator".format(generationType))
      return None
    else:
      outputPathTemplate = outputPathTemplates[generationType]
  else:
    outputPathTemplate = generationDetails['outputPathTemaplate']

  outputPathTemplate.insert(0, distDir)
  outputPathTemplate = os.path.join(*outputPathTemplate)
  outputDir = os.path.dirname(outputPathTemplate)
  
  return [ outputDir, outputPathTemplate ]

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
  if 'genSchema' not in config :
    return
  if 'pydantic' not in config['genSchema'] :
    return

  outputDir, outputPathTemplate = getOutputPaths(
    config['options'], 'pydantic', config['genSchema']['pydantic'])
  if outputDir is None :
    return

  for aRootType, aJsonSchema in jsonSchemaGenerator(interfaceDefinition) :
    outputPath = outputPathTemplate.format(aRootType)
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

def runSchemaTemplates(config, interfaceDefinition) :
  interfaceName = interfaceDefinition['name']
  #
  # setup the collection of generators for our use...
  #
  generatorOptions = copy.deepcopy(config)
  options = generatorOptions['options']
  generatorOptions = generatorOptions['genSchema']
  del generatorOptions['pydantic']
  
  for generationType, generationDetails in generatorOptions.items() :

    theTemplate, jinjaTemplatePath = loadTemplate(
      options, generationType, generationDetails)
    if theTemplate is None :
      continue
      
    outputDir, outputPathTemplate = getOutputPaths(
      options, generationType, generationDetails)
    if outputDir is None :
      continue
      
    for aRootType, aJsonSchema in jsonSchemaGenerator(interfaceDefinition) :
      outputPath = outputPathTemplate.format(aRootType)
      os.makedirs(outputDir, exist_ok=True)
      print("Generating {} {} to {}".format(generationType, aRootType, outputPath))
      print("---------------------------------------------------------")

      generationDetails['interfaceName'] = interfaceName
      generationDetails['rootType'] = aRootType
      try : 
        renderedStr = theTemplate.render({
          'options' : generationDetails,
          'schema'  : aJsonSchema,
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
  generatorOptions = generatorOptions['genExamples']

  for generationType, generationDetails in generatorOptions.items() :

    theTemplate, jinjaTemplatePath = loadTemplate(
      options, generationType, generationDetails)
    
    outputDir, outputPathTemplate = getOutputPaths(
      options, generationType, generationDetails)
    if outputDir is None :
      continue

    outputPath = outputPathTemplate.format(interfaceName)
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
        'options'  : generationDetails,
        'examples' : jsonExamples,
      })
      with open(outputPath, 'w') as outFile :
        outFile.write(renderedStr)
    except Exception as ex :
      print("Could not render the Jinja2 template [{}] using the {} jsonExamples".format(jinjaTemplatePath, interfaceName ))
      print(ex)
