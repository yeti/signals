manticom-coreDataGenerator
==========================

A Script for auto generating Core Data models and RestKit code with an API schema file

### Requirements

1. Install Xcode command line tools
2. pip install lxml (recommended to use python virtualenvs)

### Issues

1. Duplicate relationship names if a model has 2+ relationships to the same object
2. Need to appropriately generate the whole DataModel.m file (DateModel.h is done)
3. Core Data migrations when creating new objects
4. Proper dialog for asking to make core data models and relative paths to your core data config file
5. Overwrite DataModel file instead of copy/paste
6. One to one relationships
7. Optional Auth

### Instructions

1. Run python manticom_ios_coredata.py, enable xml if the objects have changed
2. If you changed the core data models, you'll need to have xcode auto generate the new model files
3. Copy in MachineDataModel.h to your project's DataModel.h
4. Copy in the appropriate sections of MachineDataModel.m to your project's DataModel.m

### Improvements

1. DELETEs
2. Refactor all the things
3. Can we automate refreshing core data?
4. Use templates instead of writing to files line by line