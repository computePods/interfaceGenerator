# ComputePods interface format

<!-- toc -->

The interface format consists of a 
[Markdown](https://en.wikipedia.org/wiki/Markdown) file with embedded
[YAML](https://en.wikipedia.org/wiki/YAML) code blocks. 

The Markdown structure of the overall description provides the developers 
with a human readable *description* of each interface. 

The embedded YAML code blocks describe sections of the overall interface 
in a precise *machine readable format* which is not too difficult for a 
human developer to read and understand. 

The outer level of the YAML for an interface consists of a YAML dictionary 
containing four keys: 

1. **`jsonTypes`** The `jsonTypes` is a YAML dictionary of individual JSON 
   types defined using a YAMLized JSON schema format
   ([see below](#yamlized-json-schema-format))

2. **`jsonExamples`** The `jsonExamples` is a YAML dictionary containing 
   YAML arrays of JSON examples for each major JSON type. These examples 
   can be used in automated testing of the interfaced components. 

3. **`httpRoutes`** The `httpRoutes` is a YAML dictionary of individual HTTP 
   routes. Each route object is a YAML dictionary of HTTP actions 
   (GET/PUT). Each HTTP action is a YAML dictionary describing the 
   route/action and the type of its expected JSON payload and response (if 
   any). Each JSON type MUST be described in the `jsonTypes` dictionary. 

   **Question**: Since the http route orders tend to be significant, 
   should this be an ordered array (or can we simply order the keys)?
   
   **Answer**: We will use a YAML dictionary for the collection of routes, 
   but each route will have a numeric "priority" field. The collection of 
   routes will be sorted by priority and then the route (as a string). 

4. **`natsChannels`** The `natsChannels` is a YAML dictionary of NATS 
   channels. Each channel is a YAML dictionary describing the channel and 
   the type of its expected JSON payloads and responses (if any). Each 
   JSON type MUST be described in the `jsonTypes` dictionary. 

The parsing and validation of the JSON payloads will be done using 
[AJV](https://ajv.js.org/) (for JavaScript) and 
[datamodel-code-generator](https://github.com/koxudaxi/datamodel-code-generator) +
[pydantic](https://pydantic-docs.helpmanual.io/) (for Python). 

## YAMLized JSON schema format

The YAML description of each JSON type is an abbreviated form of the full 
[JSON schema](http://json-schema.org/). That is, once processed by the 
interface generator, the result is a JSON schema format sufficient for the 
use with both [AJV](https://ajv.js.org/json-schema.html) and 
[datamodel-code-generator](https://koxudaxi.github.io/datamodel-code-generator/). 

However, to allow a useful abbreviated JSON schema using YAML, we wrap all 
JSON schema keywords with a leading and trailing underscore `_`. 

JSON types consist of a YAML dictionary of properties. The key for each 
field is the (string) *name* of the field. The value of each field is a 
YAML dictionary consisting of: 

- **\_type\_**: the string name of the JSON type of the field. This string 
                name may be for a simple or complex JSON type. Complex 
                JSON types MUST be defined in the `jsonTypes` dictionary. 

- **\_default\_**: an optional simple (string) expression which when 
                   evaluated produces the default value. 

- **\_items\_**: if *\_type\_* is either 'dictionary' or 'array', the JSON 
                 type of each individual dictionary or array entry. 

- **\_properties\_**: if *\_type\_* is 'object', a YAML dictionary of 
                      fieldName/JSONTypes. 
                      
- **JSON schema keywords**: any other JSON schema keywords (wrapped in 
                            leading and trailing underscore `_` 
                            characters).
                            ([See below](#json-schema-keywords)).

### Abbreviations

*If* a JSON type is a simple type, that is neither a dictionary nor an 
array, which also has no defaults or other JSON schema keywords, *then* 
the field's value may be abbreviated as the (string) name of a JSON type. 

*If* a JSON type is an array with no defaults or other JSON schema 
keywords, *then* the field's value may be abbreviated as a YAML dictionary 
with one key `_array_` whose value is the JSON type of the array's 
elements. 

*If* a JSON type is a dictionary with no defaults or other JSON schema 
keywords, *then* the field's value may be abbreviated as a YAML dictionary 
with one key `_dictionary_` whose value is the JSON type of the 
dictionary's elements. ***NOTE*** that JSON schema *do not* have 
"dictionary" types. We automagically map our "dictionaries" to JSON 
schemas of type "object" whose "additionalProperties" are our dictionary's 
_items_. (See the StackOverflow [Dictionary-like JSON 
schema](https://stackoverflow.com/questions/27357861/dictionary-like-json-schema) 
question). 

### JSON schema resources

The [JSON schema](http://json-schema.org) site itself has a number of very 
accessible [introductions](http://json-schema.org/learn/) to its schema. 

Of particular use to us is the [Structuring a complex 
schema](http://json-schema.org/understanding-json-schema/structuring.html)
chapter which is part of the larger [Understanding JSON 
Schema](http://json-schema.org/understanding-json-schema/index.html) book.

In addition there are the
[JSON Schema Core](http://json-schema.org/draft/2020-12/json-schema-core.html),
[JSON Schema Validation](http://json-schema.org/draft/2020-12/json-schema-validation.html) and
[Relative JSON Pointers](http://json-schema.org/draft/2020-12/relative-json-pointer.html)
specifications. 

### JSON schema keywords

The following is a list of the JSON schema keywords which the interface 
generator tool recognizes (there may be other keywords defined by the JSON 
schema specification which we do not have need to use).

- **preamble keywords**: $id, $schema, $vocabulary,

- **annotation keywords**: description, title

- **assertion keywords**: type, enum, const, multipleOf, maximum, 
  exclusiveMaximum, minimum, exclusiveMinimum, maxLength, minLength, 
  pattern, maxItems, minItems, uniqueItems, maxContains, minContains, 
  maxProperties, minProperties, required, dependentRequired 

- **applicator keywords**: $ref

Note that this list and categoraization is *not* definitive.