# ComputePods interface generator

A simple Python tool to generate computer readable Python and JavaScript 
interfaces from Markdown/YAML descriptions. 

Each interface description will consist of a 
[Markdown](https://en.wikipedia.org/wiki/Markdown) file with embedded 
[`YAML`](https://en.wikipedia.org/wiki/YAML) code blocks. 

The Markdown will be used for any general descriptions targeted at human 
programmers. 

The `generateInterface` tool will extract the embedded `YAML` code blocks, 
load as `YAML` and use it to produce the required interfaces descriptions 
for use by the JavaScript (browser based UI) and Python (server). 

The ComputePods [interfaces](https://github.com/computePods/interfaces) 
project is the primary collection of interfaces for the 
[ComputePods](https://github.com/computePods) tools. 

For more details see [docs/Readme.md](docs/Readme.md)