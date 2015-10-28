signals
=================

| |Codeship Status for yeti/signals|
| |Coverage Status|

A tool for auto generating libraries for different platforms to
communicate with your API.

Recommended Setup
-----------------

#. Create a new python virtual environment
#. ``pip install yak-signals``

Instructions
------------

The script is ran from ``signals``.

To see a list of arguments run ``signals --help``.

If you do not supply the required arguments when running, the script
will prompt you for them one by one.

An example for running the script is::

  signals --schema ~/projects/your-project/api-schema.json
  --datamodels ~/projects/your-project/data-model-folder/
  --coredata ~/projects/your-project/core-data.xcdatamodeld
  --projectname your-project --generator objc

iOS
~~~

#. If you’re running the iOS generator and writing to core data make
   sure you quit xcode
#. Run ``signals``, and pass the ``--coredata`` flag
   if you want to override core data.
#. If you changed the core data models, you’ll need to have xcode auto
   generate the new model files

.. |Codeship Status for yeti/signals| image:: https://codeship.com/projects/d2fa74a0-01ab-0133-75b8-2226f6cba81b/status?branch=master
   :target: https://codeship.com/projects/88715
.. |Coverage Status| image:: https://coveralls.io/repos/yeti/signals/badge.svg?branch=master&service=github
   :target: https://coveralls.io/github/yeti/signals?branch=master