
# For file inclusion consider:
#   https://github.com/jreese/markdown-pp

import click
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

def normalizeJsonTypes(abbreviatedJsonType) :
  return abbreviatedJsonType

def mergeYamlData(yamlData, newYamlData, thePath) :
  if type(yamlData) is None :
    print("ERROR yamlData should NEVER be None ")
    sys.exit(-1)
    
  if type(yamlData) != type(newYamlData) :
    print("Incompatible types {} and {} while trying to merge YAML data at {}".format(type(yamlData), type(newYamlData), thePath))
    print("Stoping merge at {}".format(thePath))
    return

  if type(yamlData) == 'dictionary' :
    for key, value in newYamlData.items() :
      if key not in yamldata :
        yamlData[key] = value
      elif type(yamlData[key]) == 'dictionary' :
        mergeYamlData(yamlData[key], value, thePath+'.'+key)
      elif type(yamldata[key]) == 'array' :
        yamlData[key].append(value)
      else
        yamlData[key] = value
  elif type(yamlData) == 'array' :
    for value in newYamlData :
      yamlData.append(value)
  else 
    print("ERROR yamlData MUST be either a dictionary or an array.")
    sys.exit(-1)

def addYamlBlock(yamlLines) :
  if -1 <  yamlLines[0].lower().find('example') :
    return  # we ignore all yaml blocks with 'example' in the first line
    
  newYamlData = None
  try :
    newYamlData = yaml.safe_load("\n".join(yamlLines))
  except:
    print("Could not parse the YAML code block: ")
    print("\n  ".join(yamlLines))
  if newYamlData is None :
    return # there is no yaml data (that we could parse) in this block

  if type(newYamlData) is not 'dictionary' :
    print("The YAML block MUST be a dictionary")
    return

  if 'jsonTypes' in newYamlData :
    newYamlData = normalizeJsonTypes(newYamlData)
  elif 'httpRoutes' in newYamlData :
    # no normalization needed
  elif 'natsChannels' in newYamlData :
    # no normalization needed
  else :
    print("The YAML block must contain a 'jsonTypes', 'httpRoutes' or 'natsChannel' definition.")
    return

  mergeYamlData(interfaceDescription, newYamlData, "")
 
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

  print("Working on {}".format(interface_name))
  interface = open(interface_name)
  lines = interface.readlines()
  interface.close()
  insideYaml = False
  theYaml = []
  theMarkdown = []
  for line in lines :
    line = line.rstrip()
    if insideYaml :
      if line != "```" :
        theYaml.append(line)
      else :
        addYamlBlock(theYaml)
        insideYaml = False
    else :
      if line != "```yaml" :
        theMarkdown.append(line)
      else :
        insideYaml = True

  print("---------------------------------------------------------")
  print("\n".join(theMarkdown))
  print("---------------------------------------------------------")
  print(yaml.dump(interfaceDescription))
  print("---------------------------------------------------------")