# ComputePods interface generation design

<!-- toc -->

Once the description of an interface has been loaded, the interface 
generator tool uses [Jinja2](https://jinja2docs.readthedocs.io/en/stable/) 
templates to generate various interface code files. 

At the moment the interface generator generates the follow types of code:

- JSON type definition in [Python 
  pydantic](https://pydantic-docs.helpmanual.io/) format using
  [datamodel-code-generator](https://github.com/koxudaxi/datamodel-code-generator)

  Consider using the companion
  [fastapi-code-generator](https://github.com/koxudaxi/fastapi-code-generator)

- JSON example data in Python format

- JSON type definition in JavaScript formatted using 
  [AJV](https://ajv.js.org/) 

- JSON example data in JavaScript format

- HTTP routes mocked in JavaScript using [Mock Service 
  Workers](https://mswjs.io/docs/)

- HTTP mount points expressed as Mithril mixin components.
