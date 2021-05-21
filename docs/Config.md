# ComputePods interface generator configuration

<!-- toc -->

The ComputePods interface generator is primarily configured using a 
[YAML](https://en.wikipedia.org/wiki/YAML) configuration file. 

By default this configuraiton file is called `cpigConfig.yaml` in the 
directory in which the tool is started. Alternatively you can use the `-c` 
or `--config` command line option to specify a different configuration 
file. 

This configuration file works by having or not having one or more 
hierarchies of values. 

## Controlling where the output code files go

To specify the directory in which to place output code add the following key:

```yaml
output: <aPath>
```

where `<aPath` is either an absolute path in your file system, or a path 
relative to the current working directory (in which you run the tool). 

## Producing Pydantic/Python classes

To produce [Pydantic](https://pydantic-docs.helpmanual.io/) data classes 
for use in Python code add the following keys: 

```yaml
pydantic:
  <aCollectionOfKey>: <valuePairs>
```

You can use any of the 
[datamodel-code-generator](https://github.com/koxudaxi/datamodel-code-generator#usage) 
command line options in the above collectino of key/value pairs. If the 
option takes no arguments, then simply leave the value empty. (Note that 
any of the "input" options will be ignored as the input is controled by 
the interface generator itself). 

If you just want to use the standard defaults they add the following keys: 

```yaml
pydantic
```

## Producing AJV/JavaScript classes

To produce [AJV](https://ajv.js.org/guide/getting-started.html) parsing / 
validation / serialization code for use in JavaScript (either on the 
server or in the browser) add the following keys: 

```yaml
ajv:
  - parse
  - serialize
```

You can use either or both of the `parse` or `serialize` keywords.

## Producing JSON examples for use in JavaScript

To produce JSON examples for use in JavaScript add the following keys:

```yaml

javaScriptExamples

```

## Producing JSON examples for use in Python

To produce JSON examples for use in Python add the following keys:

```yaml
pythonExamples
```
## Producing Mock Service Workers for use in JavaScript

To produce Mock Service Workers code from the `httpRoutes` and 
`jsonExamples` then add the following keys:

```yaml
mockServiceWorkers
```

## Full example with Pydantic defaults

To produce all of the output using the Pydantic defaults use the following 
configuration file: 

```yaml
pydantic

ajv:
  - parse
  - serialize

javaScriptExamples

pythonExamples

mockServiceWorkers
```
