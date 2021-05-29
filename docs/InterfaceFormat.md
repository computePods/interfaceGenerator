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

The outer level of the YAML for an interface consists of a dictionary 
containing five keys: 

1. **`jsonSchemaPreamble`** The (optional) `jsonSchemaPreamble` is a 
   dictionary of the JSON Schema preambles for each of the root classes 
   to be built. The keys in the dictionary associated with each root class 
   consist of the JSON schema preamble definitions for that root class's 
   whole schema. 

2. **`jsonSchemaDefs`** The `jsonSchemaDefs` is a  dictionary of 
   individual JSON types defined using a YAMLized JSON schema format ([see 
   below](#yamlized-json-schema-format)) 

3. **`jsonExamples`** The `jsonExamples` is a  dictionary containing 
   arrays of JSON examples for each major JSON type. These examples can be 
   used in automated testing of the interfaced components. 

4. **`httpRoutes`** The `httpRoutes` is a  dictionary of individual HTTP 
   routes. Each route object is a dictionary of HTTP actions (GET/PUT). 
   Each HTTP action is a dictionary describing the route/action and the 
   type of its expected JSON payload and response (if any). Each JSON type 
   MUST be described in the `jsonSchemaDefs` dictionary. 

   **Question**: Since the HTTP route orders tend to be significant, 
   should this be an ordered array (or can we simply order the keys)?
   
   **Answer**: We will use a  dictionary for the collection of routes, 
   but each route will have a numeric "priority" field. The collection of 
   routes will be sorted by priority and then the route (as a string). 

5. **`natsChannels`** The `natsChannels` is a dictionary of NATS channels. 
   Each channel is a dictionary describing the channel and the type of its 
   expected JSON payloads and responses (if any). Each JSON type MUST be 
   described in the `jsonSchemaDefs` dictionary. 

The parsing and validation of the JSON payloads will be done using 
[AJV](https://ajv.js.org/) (for JavaScript) and 
[datamodel-code-generator](https://github.com/koxudaxi/datamodel-code-generator) +
[pydantic](https://pydantic-docs.helpmanual.io/) (for Python). 

## YAMLized JSON schema format

The YAMLized description of each JSON type is essentially that fragment 
of the full [JSON schema](http://json-schema.org/) which is needed to 
define *one* JSON type. Once processed by the interface generator, the 
combination of the `jsonSchemaPreamble` and the `jsonSchemaDefs` is a JSON 
schema format sufficient for the use with both 
[AJV](https://ajv.js.org/json-schema.html) and 
[datamodel-code-generator](https://koxudaxi.github.io/datamodel-code-generator/). 

Once processed into valid JSON schema, the `jsonSchemaDefs` definitions 
are placed into a standard JSON schema `$defs` dictionary. This means the 
cross references to types defined in this interface schema, can be done 
using the standard (internal) reference notation: 

```
  $ref: "#/$defs/<nameOfJsonType>"
```

To help express the overall semantic meaning of the `jsonSchemaDefs` we 
add a `dictionary` type to the "valid" schema. This `dictionary` type must 
have an associated `items` key. This `dictionary` type is then transformed 
into valid JSON schema as suggested by the StackOverflow [Dictionary-like 
JSON 
schema](https://stackoverflow.com/questions/27357861/dictionary-like-json-schema) 
question. 

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
generator tool recognises (there may be other keywords defined by the JSON 
schema specification which we do not have need to use).

- **preamble keywords**: $id, $schema, $vocabulary,

- **annotation keywords**: description, title, deprecated, readOnly, 
  writeOnly, examples 

- **assertion keywords**: type, enum, const, multipleOf, maximum, 
  exclusiveMaximum, minimum, exclusiveMinimum, maxLength, minLength, 
  pattern, maxItems, minItems, uniqueItems, maxContains, minContains, 
  maxProperties, minProperties, required, dependentRequired 

- **applicator keywords**: $ref

Note that this list and categorisation is *not* definitive.