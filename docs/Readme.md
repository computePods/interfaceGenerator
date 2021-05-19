# ComputePods interface generator

<!-- toc -->

The ComputePods interface generator is used to generate a collection of 
RESTful (HTTP) as well as NATS (publish/subscribe and request/response) 
JSON based interfaces. 

It uses a Litterate definition style based upon a mixture of Markdown and 
YAML formated files. 

The Markdown structure of the overall description provides the developers 
with a human readable description of each interface. 

This Markdown contains embedded YAML code blocks. Each code bock describes 
sections of the overall interface. (YAML code blocks which contain the 
word "example" in the first line are ignored). 

The outer level of the YAML for an interface consists of a dictionary 
containing three keys:

1. **`jsonTypes`** The `jsonTypes` is a dictionary of individual JSON 
   types using a description similar to 

2. **`httpRoutes`** The `httpRoutes` is an dictionary of individual HTTP 
   routes. Each route object is a dictionary of HTTP actions (GET/PUT). 
   Each HTTP action is a dictionary describing the route/action and the 
   type of its expected JSON payload and response (if any). Each JSON type 
   MUST be described in the `jsonTypes` dictionary. 

   **Question**: Since the http route orders tend to be significant, 
   should this be an ordered array (or can we simply order the keys)?

3. **`natsChannels`** The `natsChannels` is a dictionary of NATS channels. 
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

JSON types consist of an dictionary of fields. The key for each field is 
the (string) *name* of the field. The value of each field is a dictionary 
consisting of: 

- **type**: the JSON type of the field (which may be either the string 
            name of a simple or complex JSON type)

- **default**: an optional simple (string) expression which when evaluated 
               produces the default value. 

- **keys**: if *type* is a dictionary, the JSON type of the keys of the 
            dictionary. 

- **items**: if *type* is either a dictionary or an array, the JSON type 
             of each indivicual dictionary or array entry.

#### Abbreviations

*If* a JSON type is a simple type, that is neither a dictionary nor an 
array, which also has no defaults, *then* the field's value may be 
abbreviated as the (string) name of a JSON type. 

*If* a JSON type is a dictionary with no defaults and whose keys are all 
strings, *then* the field's value may be abbreviated as a dictionary with 
one key `__dictionary__` whose value is the JSON type of the dictionary's 
elements. 

*If* a JSON type is an array with no defaults, *then* the field's value 
may be abbreviated as a dictionary with one key `__array__` whose value is 
the JSON type of the array's elements. 
