manticom-coreDataGenerator
==========================

A Script for auto generating Core Data models and RestKit code with an API schema file

### Requirements

1. Install Xcode command line tools
2. pip install lxml (recommended to use python virtualenvs)

### Issues

1. Duplicate field names if they have a field, as well as a relationship
2. Need to appropriately generate the whole DataModel.m file (DateModel.h is done)
3. Proper dialog for asking to make core data models and relative paths to your core data config file
4. Overwrite DataModel file instead of copy/paste
5. One to one relationships


### Instructions

1. If you're running the core data xml part of the script, exit xcode before running or restart afterwards
2. Run python manticom_ios_coredata.py, enable xml if the objects have changed
3. If you changed the core data models, you'll need to have xcode auto generate the new model files
4. Copy in MachineDataModel.h to your project's DataModel.h
5. Copy in the appropriate sections of MachineDataModel.m to your project's DataModel.m

### Improvements

1. Refactor all the things
2. Can we automate refreshing core data?
3. Use templates instead of writing to files line by line
4. Core Data migrations when creating new objects
5. Optional Auth