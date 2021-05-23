
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
    options = config['options']
    outputPath = os.path.join(options['codeDirs']['python'], aRootType+options['codeExts']['python'])
    os.makedirs(options['codeDirs']['python'], exist_ok=True)
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


def runTemplates(config, interfaceDefinition) :
  #
  # setup the collection of generators for our use...
  #
  generatorOptions = copy.deepcopy(config)
  options = generatorOptions['options']
  del generatorOptions['options']
  del generatorOptions['pydantic']

  
  for generationType, generationDetails in generatorOptions.items() :
    generationFileName = generationType + '.j2'
    print(generationType)
    print(generationFileName)
    print(yaml.dump(generationDetails))

    jinjaTemplatePath = None
    if 'jinja2' in generationDetails :
      jinjaTemplatePath = generationDetails['jinja2']
      del generationDetails['jinja2']

    theTemplateStr = None
    if jinjaTemplatePath and os.path.exists(jinjaTemplatePath) :
      with open(jinjaTemplatePath, 'r') as jinjaFile :
        theTemplateStr = jinjaFile.read()
    else :
      if importlib.resources.is_resource('cpig.templates', generationFileName) :
        theTemplateStr = importlib.resources.read_text('cpig.templates', generationFileName)

    if jinjaTemplatePath is None :
      jinjaTemplatePath = 'cpig/'+generationFileName

    if not theTemplateStr :
      if options['verbose'] :
        print("No jinja2 template found for {} [{}]".format(generationType, jinjaTemplatePath))
        continue
    try : 
      theTemplate = jinja2.Template(theTemplateStr)
    except Exception as ex :
      print("Could not create the Jinja2 template [{}]".format(jinjaTemplatePath))
      print(ex)

    codeTypes = options['codeTypes']
    if generationType not in  codeTypes :
      print("Could not determine the type of code for the {} code generator".format(generationType))
      continue
    codeType = codeTypes[generationType]
    
    codeDirs = options['codeDirs']
    if codeType not in codeDirs :
      print("Could not determine the output directory for the {} code generator".format(generationType))
      continue
    outputDir = codeDirs[codeType]

    codeExts = options['codeExts']
    if codeType not in codeExts :
      print("Could not determine the output file extension for the {} code generator".format(generationType))
      continue
    codeExt = codeExts[codeType]

    for aRootType, aJsonSchema in jsonSchemaGenerator(interfaceDefinition) :
      outputPath = os.path.join(outputDir, aRootType+codeExt)
      os.makedirs(outputDir, exist_ok=True)
      print("Generating {} {} to {}".format(generationType, aRootType, outputPath))
      print("---------------------------------------------------------")
    
      try : 
        renderedStr = theTemplate.render({
          'options' : generationDetails,
          'schema'  : aJsonSchema,
          'schemaStr' : json.dumps(aJsonSchema, sort_keys=True, indent=2)
        })
        with open(outputPath, 'w') as outFile :
          outFile.write(renderedStr)
      except Exception as ex :
        print("Could not render the Jinja2 template [{}] using the {} JSON Schema".format(jinjaTemplatePath, aRootType ))
        print(ex)
      
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