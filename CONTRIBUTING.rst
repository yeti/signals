YAK-communication
=================

|Codeship Status for yeti/signals| |Coverage Status|

Recommended Development Setup
-----------------------------

1. Create a new python virtual environment
2. ``pip install -r requirements.txt``
3. ``pip install -r dev-requirements.txt``

Instructions
------------

The script is ran from ``python -m signals``.

Development
-----------

- To run the tests, just run ``nosetests``.

TODOs
-----

- Generate RestKit code in Swift instead of Objective C
- Build other generators!
- Auto-generate API schemas and/or Improve current API schema and remove unnecessary parts

    - Our comma delimited lists can just become real attributes and flags now
    - No need to have our objects wrapped in an extra dictionary

- Better error checking and validation
- Figure out a best-way to handle generator specific arguments (click has some utilities built-in for prompting)
- Documentation (ex. a demo app w/ demo api schema file)
- Use something like https://github.com/rentzsch/mogenerator to auto generate core data files
- Don't require the user to have the api-schema file on their computer but point to a URL
- Preserve existing edits to core data or data model file.
- Use a decorator system to register template methods so we can better organize our code
- Setup pep8 and pyflakes testing for coding style guide enforcement
- Refactor use of '$names' and how API objects get a reference to the actual object


.. |Codeship Status for yeti/signals| image:: https://codeship.com/projects/d2fa74a0-01ab-0133-75b8-2226f6cba81b/status?branch=master
   :target: https://codeship.com/projects/88715
.. |Coverage Status| image:: https://coveralls.io/repos/yeti/signals/badge.svg?branch=HEAD&t=YrPM9o
   :target: https://coveralls.io/r/yeti/signals?branch=HEAD