# Mithril Connectors

Each [Mithril](https://mithril.js.org/) Connector is a [Mithril
Component](https://mithril.js.org/components.html) which *models* the
state of an entity in one or more ComputePod servers for the MajorDomo UI.

Each Mithril Connector embeds the artefact URL for the entity it
represents. It also defines default RESTful methods to get or set the
server data. These default methods can be over-ridden or wrapped by the
MajorDomo UI for more specialsized purposes.

The MajorDomo UI Mithril interface view methods corresponding to each
entity type, expects to display the entity by accessing the entity's
`data` field.

There are two flavours of our use of the RESTful "get" method. HTTP GET
requests which contain no embedded payload will receive the *whole*
representation of the entity in the JSON response. HTTP GET requests which
contain an embedded JSON payload describing what part of the repsentation
the UI already has, will receive only the requested sub-part of the
entity's representation.

The Mithril Connector implements three distinct "get" methods:

1. `getAllServerData`
2. `getChangedServerData`
3. `_getServerData`

The (private) `_getServerData` method initiates an HTTP GET [Mithril
Request](https://mithril.js.org/request.html) on the entity's embedded
artefact URL, with the JSON payload taken from the entity's
'updateRequest' field (if this field is not `null`) and returns the
associated [Mithril Promise](https://mithril.js.org/promise.html).

The `getAllServerData` method simply clears `updateRequest` field (setting
it to `null`), calls the `_getServerData` and uses the returned promise to
copy the request's response into the `data` field as a whole.

The *default* `getChangedServerData` behaves identically to the
`getAllServerData` method (for most cases where the entity's structure is
small or complex, this is sufficient). The MajorDomo UI can override this
`getChangedServerData` method as needed. For example, for logFile
entities, the `getChangedServerData` may set the `updateRequest` field
with the last known "logFile line", call the `_getServerData` and then
append the new "logFile lines" (contained in the promised request's
response) to the end of the existing logFile lines in the `data` field.