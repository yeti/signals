Get Started
===========

Signals is a tool that will automatically generate front-end code for you based on a JSON schema file. This means that you can simply define your API endpoints, and if they change, you can just update the JSON schema, run signals, and have your front-end update to reflect the changes. No more need to write boilerplate code to define your models or how they talk to your server. Signals is backend-agnostic, and can be used for Django, Rails, Node, etc. apps.

#. Signals is written in Python. You'll need Python on your machine if you don't have it yet.
#. ``pip install yak-signals``
#. To see if signals successfully installed, run ``signals --help``
#. To run signals, you just need to specify the JSON schema file you want to use, what sort of code you want to generate (ObjC, Angualar, etc.), and any options for that generator

See below for specific instructions for each generator.

.. _getting-started-ios:

iOS
---

Currently, our iOS generator assumes you are using Objective-C, Core Data, and Restkit. If you have a different setup (Alamofire, Swift, etc.), see the section on :ref:`writing-your-own-template`.

#. If your API changes will affect Core Data (e.g., you are changing the fields you receive as a response to a call):
    - Make sure you first quit Xcode
    -  Run ``signals`` and pass the ``--coredata`` flag (e.g., ``signals --schema ~/path/to/schema.json --generator ios --coredata``) (TODO: is this how you do it?)
    - If you changed the core data models, you’ll need to have xcode auto generate the new model files (TODO: someone mention how to do this)
#. If you're not changing Core Data, just run signals: ``signals --schema ~/path/to/schema.json --generator ios``  (TODO: is this how you do it?)