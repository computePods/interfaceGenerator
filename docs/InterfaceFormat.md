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

   The YAMLized schema for `jsonSchemaPreamble` is as follows:

   ```yaml
     jsonSchemaPreamble:
       # is a dictionary of jsonType -> JSON Schema preamble strings
       type: dictionary
       items:
         type: dictionary
         items:
           type: string
   ```

2. **`jsonSchemaDefs`** The `jsonSchemaDefs` is a  dictionary of 
   individual JSON types defined using a YAMLized JSON schema format ([see 
   below](#yamlized-json-schema-format)) 

   The YAMLized schema for `jsonSchemaDefs` is as follows:
   
   ```yaml
     jsonSchemaDefs:
       # is a dictionary of jsonType -> JSON Schema definitions
       type: dictionary
       items: 
         type: draft7  # A (draft 7) JSON Schema
   ```

3. **`jsonExamples`** The `jsonExamples` is a  dictionary containing 
   arrays of JSON examples for each major JSON type. These examples can be 
   used in automated testing of the interfaced components. 

   The YAMLized schema for the *header* of one `jsonExamples` is as 
   follows: 
   
   ```yaml
     jsonExamplesHeader:
       # is a dictionary of jsonType -> http route fragments
       type: object
       properties:
         title:
           type: string
         httpRoutes:
           type: object
           properties:
             # an httpRoute fragment is a object of:
             #  - an example route (url)
             #  - an action
             route:
               type: string
             action:
               enum:
                - GET
                - POST
                - PUT
                - DELETE
    ```
 
4. **`httpRoutes`** The `httpRoutes` is a dictionary of server HTTP mount 
   points. Associated with each mount point is a JSON object with the 
   properties `body` (which is the *name* of a `jsonType` in the 
   `jsonSchemaDefs`), `url` (a string URL template for the mount point), 
   `actions` (an array of `GET`, `POST`, `PUT` and `DELETE` HTTP actions). 
   The `body` `jsonType` is expected JSON payload and response (if any). 
   Each JSON type MUST be described in the `jsonSchemaDefs` dictionary. 

   **Question**: Since the HTTP route orders tend to be significant, 
   should this be an ordered array (or can we simply order the keys)?
   
   **Answer**: We will use a  dictionary for the collection of routes, 
   but each route will have a numeric "priority" field. The collection of 
   routes will be sorted by priority and then the route (as a string). 

   The YAMLized schema for `httpRoutes` is as follows:
   
    ```yaml 
     httpRoutes:
       # is a dictionary of mountPoints -> httpRoutes 
       type: dictionary
       items:
         # an httpRoute is a dictionary of:
         #  - a list of actions (GET, POST, PUT, DELETE)
         #  - a declaration of the request/response body format 
         #    as a jsonType in the jsonSchemaDefs
         #  - the url template (which may include <name> elements)
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
             # the url template for this mount point
             type: string 
           actions:
             type: array
             items:
               enum:
                 - GET
                 - POST
                 - PUT
                 - DELETE
   ```

5. **`natsChannels`** The `natsChannels` is a dictionary of NATS channels. 
   Each channel is a dictionary describing the channel and the type of its 
   expected JSON payloads and responses (if any). Each JSON type MUST be 
   described in the `jsonSchemaDefs` dictionary. 

   The YAMLized schema for `natsChannels` is as follows:
   
   ```yaml
     natsChannels: { }
       # is a dictionary of NATS channels -> ????
   ```
   
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