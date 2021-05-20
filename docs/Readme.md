# ComputePods interface generator

<!-- toc -->

The ComputePods interface generator is used to generate a collection of 
[RESTful 
(HTTP)](https://en.wikipedia.org/wiki/Representational_state_transfer) as 
well as [NATS (publish/subscribe and 
request/response)](https://docs.nats.io/) interfaces. All of these
interfaces will use [JSON payloads](https://en.wikipedia.org/wiki/JSON).

It uses a [Litterate definition 
style](https://en.wikipedia.org/wiki/Literate_programming) based upon a 
mixture of [Markdown](https://en.wikipedia.org/wiki/Markdown) and 
[YAML](https://en.wikipedia.org/wiki/YAML) formated files. 

The Markdown structure of the overall description provides the developers 
with a human readable description of each interface. 

This Markdown contains embedded YAML code blocks. Each code bock describes 
sections of the overall interface. (YAML code blocks which contain the 
word "example" in the first line are ignored). 

The outer level of the YAML for an interface consists of a dictionary 
containing four keys:

1. **`jsonTypes`** The `jsonTypes` is a dictionary of individual JSON 
   types using a description similar to 

2. **`jsonExamples`** The `jsonExamples` is dictionary containing arrays 
   of JSON examples for each major JSON type. These examples can be used 
   in automated testing of the interfaced components. 

3. **`httpRoutes`** The `httpRoutes` is an dictionary of individual HTTP 
   routes. Each route object is a dictionary of HTTP actions (GET/PUT). 
   Each HTTP action is a dictionary describing the route/action and the 
   type of its expected JSON payload and response (if any). Each JSON type 
   MUST be described in the `jsonTypes` dictionary. 

   **Question**: Since the http route orders tend to be significant, 
   should this be an ordered array (or can we simply order the keys)?

4. **`natsChannels`** The `natsChannels` is a dictionary of NATS channels. 
   Each channel is a dictionary describing the channel and the type of its 
   expected JSON payloads and responses (if any). Each JSON type MUST be 
   described in the `jsonTypes` dictionary. 

The validation of the JSON types will be done using 
[AJV](https://ajv.js.org/) (for JavaScript) and
[dataclasses](https://docs.python.org/3/library/dataclasses.html) (for 
Python). 

### Existing JSON type specifications

Currently there are three 'official' standards for specifying JSON types 
we might consider "using": 

- **[JSON schema](http://json-schema.org/)**, we might use [AJV's 
  variant](https://ajv.js.org/json-schema.html),

- **[JSON type definitions](https://datatracker.ietf.org/doc/rfc8927/)** 
  When generating AJV validators, we will target [AJV's 
  variant](https://ajv.js.org/json-type-definition.html).

- **[Python dataclasses](https://docs.python.org/3/library/dataclasses.html)**

### Our YAML based JSON type specification

The YAML description of each JSON type will essentially be based upon a 
the Python `dataclasses` format.

JSON types consist of a dictionary of fields. The key for each field is 
the (string) *name* of the field. The value of each field is a dictionary 
consisting of: 

- **\_type\_**: the JSON type of the field (which may be either the string 
                name of a simple or complex JSON type)

- **\_default\_**: an optional simple (string) expression which when 
                   evaluated produces the default value. 

- **\_keys\_**: if *\_type\_* is 'dictionary', the JSON type of the keys 
              of the dictionary. In the current implementation all 
              dictionary keys MUST be strings. 

- **\_items\_**: if *\_type\_* is either 'dictionary' or 'array', the JSON 
                 type of each individual dictionary or array entry. 

- **\_fields\_**: if *\_type\_* is 'object', a dictionary of 
                  fieldName/JSONTypes. 

#### Abbreviations

*If* a JSON type is a simple type, that is neither a dictionary nor an 
array, which also has no defaults, *then* the field's value may be 
abbreviated as the (string) name of a JSON type. 

*If* a JSON type is a dictionary with no defaults and whose keys are all 
strings, *then* the field's value may be abbreviated as a dictionary with 
one key `_dictionary_` whose value is the JSON type of the dictionary's 
elements. 

*If* a JSON type is an array with no defaults, *then* the field's value 
may be abbreviated as a dictionary with one key `_array_` whose value is 
the JSON type of the array's elements. 
