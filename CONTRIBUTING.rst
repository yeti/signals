YAK-communication
=================

|Codeship Status for yeti/signals| |Coverage Status|

Recommended Development Setup
-----------------------------

1. Create a new python virtual environment
2. ``pip install -r requirements.txt``

Instructions
------------

The script is ran from ``python -m signals``.

Development
-----------

1. To run the tests, just run ``nosetests``.

TODOs
-----

1. Generate RestKit code in Swift instead of Objective C
2. Create a config file that will save your input for the various flags if you're inside the correct project
3. Build other generators!
4. Auto-generate API schemas and/or Improve current API schema and remove unnecessary parts

    - Our comma delimited lists can just become real attributes and flags now
    - No need to have our objects wrapped in an extra dictionary

5. Better error checking and validation
6. Figure out a best-way to handle generator specific arguments (click has some utilities built-in for prompting)
7. Documentation (ex. a demo app w/ demo api schema file)
8. Create setup.py for pip installing and make a release for pypi

    - Part of this would include making this a command you could run from anywhere (signals vs. python -m signals)

9. Use something like https://github.com/rentzsch/mogenerator to auto generate core data files
10. Don't require the user to have the ap-schema file on their computer but point to a URL
11. Preserve existing edits to core data or data model file.
12. Use a decorator system to register template methods so we can better organize our code
13. Setup pep8 and pyflakes testing for coding style guide enforcement
14. Refactor use of '$names' and how API objects get a reference to the actual object


.. |Codeship Status for yeti/signals| image:: https://codeship.com/projects/d2fa74a0-01ab-0133-75b8-2226f6cba81b/status?branch=master
   :target: https://codeship.com/projects/88715
.. |Coverage Status| image:: https://coveralls.io/repos/yeti/signals/badge.svg?branch=HEAD&t=YrPM9o
   :target: https://coveralls.io/r/yeti/signals?branch=HEAD