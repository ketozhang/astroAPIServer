# astroAPIServer
Boilerplate and toolkit to build API servers for data access and data releases Designed for astronomy research content on web apps.

Not yet released for public use

## Features
* OpenAPI Specification

  Supports OpenAPI 3 to allow complete description of the API via a JSON or YAML file.
* [Simple Image Access](http://www.ivoa.net/Documents/SIA/)

  An image accessing standard by IVOA.
* Admin console

  A tool in form of a webpage to test your API and even for your team to extract data.

## Getting Started

* Import and define `astroapiserver::API`
* Define database handling
* Create authentication and authorization databases
* Define authentication and authorization functions
* Install simplejson (`pip install simplejson`)
* Define environment variables
    * `SECRET`
    * `JWT_SECRET`
    * `JWT_EXP`
    * (Optional) Store in env.json