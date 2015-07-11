YAK-communication
=================

|Codeship Status for yeti/YAK-communication| |Coverage Status|

Recommended Development Setup
-----------------------------

1. Create a new python virtual environment
2. ``pip install -r requirements.txt``

Instructions
------------

The script is ran from ``python -m yak_communication``.

Development
-----------

1. To run the tests, just run ``nosetests``.
2. You can also run the tests with coverage:
   ``nosetests --with-coverage --cover-package=yak_communication --cover-inclusive --cover-branches``

TODOs
-----

1. Generate RestKit code in Swift instead of Objective C

   -  Use separate template files instead of inline multi-line strings
   -  Fully copy over the generated code into the iOS project
   -  Write tests for new iOS generator code

2. Create a config file that will save your input for the various flags
   if you’re inside the correct project
3. Build other generators!
4. Auto-generate API schemas and/or Improve current API schema and
   remove unnecessary parts

   -  Our comma delimited lists can just become real attributes and
      flags now
   -  No need to have our objects wrapped in an extra dictionary

5. Better error checking and validation
6. Better logging (use different terminal colors for warnings/progress
   messages)
7. Figure out a best-way to handle generator specific arguments (click
   has some utilities built-in for prompting)
8. Documentation (ex. a demo app w/ demo api schema file)

.. |Codeship Status for yeti/YAK-communication| image:: https://codeship.com/projects/d2fa74a0-01ab-0133-75b8-2226f6cba81b/status?branch=master
   :target: https://codeship.com/projects/88715
.. |Coverage Status| image:: https://coveralls.io/repos/yeti/YAK-communication/badge.svg?branch=HEAD&t=YrPM9o
   :target: https://coveralls.io/r/yeti/YAK-communication?branch=HEAD