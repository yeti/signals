YAK-communication
==========================

[ ![Codeship Status for yeti/YAK-communication](https://codeship.com/projects/d2fa74a0-01ab-0133-75b8-2226f6cba81b/status?branch=master)](https://codeship.com/projects/88715)

A tool for auto generating libraries for different platforms to communicate with your API. 

### Recommended Setup

1. Create a new python virtual environment
2. `pip install requirements.txt`


### Instructions

The script is ran from `python yak_communication/main.py`.

To see a list of arguments run `python yak_communication/main.py`.

If you do not supply the required arguments when running, the script will prompt you for them one by one.

An example for running the script is: `python yak_communication/main.py --schema ~/projects/your-project/api-schema.json --generator ios`

#### iOS

1. If you're running the iOS generator and writing to core data make sure you quit xcode
2. Run `python yak_communication/main.py`, and pass the `--coredata` flag if you want to override core data.
3. If you changed the core data models, you'll need to have xcode auto generate the new model files
4. Copy in MachineDataModel.h to your project's DataModel.h
5. Copy in the appropriate sections of MachineDataModel.m to your project's DataModel.m


### Development

1. To run the tests, just run `nosetests`.
2. You can also run the tests with coverage: `nosetests --with-coverage --cover-package=yak_communication --cover-inclusive`


### TODOs

1. Generate RestKit code in Swift instead of Objective C
    * Use separate template files instead of inline multi-line strings
    * Fully copy over the generated code into the iOS project
    * Write tests for new iOS generator code
2. Create a config file that will save your input for the various flags if you're inside the correct project
3. Build other generators!
4. Auto-generate API schemas and/or Improve current API schema and remove unnecessary parts
    * Our comma delimited lists can just become real attributes and flags now
    * No need to have our objects wrapped in an extra dictionary
5. Better error checking and validation
6. Better logging (use different terminal colors for warnings/progress messages)
7. Figure out a best-way to handle generator specific arguments (click has some utilities built-in for prompting)