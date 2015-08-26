How It Works
============
Signals has three main components:

- The parser
- The generators
- The templates

Parser
------
The parser reads your JSON schema file and translates those JSON objects into Python objects. It creates two main types of objects ``DataObject``s, which include the fields, relationships, and structure of the data your API sends, and ``URL``s with specific ``API`` endpoints associated.

Generators
----------
By and large, each generator should correspond to a front-end platform (e.g., iOS, Android, AngularJS). TODO: Better explanation of what a generator does that is separate from what the templates do

Templates
---------
We use `Jinja <http://jinja.pocoo.org/>`_, the popular Python templating engine, to produce the actual model definitions and code to make server requests. A single generator could have multiple template styles. For example, the iOS generator could have both Objective-C and Swift templates, an AngularJS generator could have templates for ``$http``, ``$resource``, and ``restangular``.