# ComputePods interface generator design

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

[The design of the interface format can be found here.](InterfaceFormat.md)

[The design of the interface generation, using Jinja2 templates, can be found here.](Generation.md)