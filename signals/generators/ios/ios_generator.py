import os
from signals.generators.ios.objectivec_template import ObjectiveCTemplate
from signals.generators.ios.swift_template import SwiftTemplate
from signals.helpers import recursively_find_parent_containing_file
import subprocess
from jinja2 import Environment, PackageLoader
from signals.logging import SignalsError, progress, warn
from signals.generators.base.base_generator import BaseGenerator
from signals.generators.ios.core_data import write_xml_to_file


class iOSGenerator(BaseGenerator):
    template_options = {
        'objc': 'Objective-C',
        'swift': 'Swift'
    }

    def __init__(self, templates, schema, data_models_path, core_data_path, project_name):
        super(iOSGenerator, self).__init__(schema)
        # Command flags
        self.data_models_path = data_models_path
        self.core_data_path = core_data_path
        self.project_name = project_name
        self.templates = templates

        # Setup
        if not os.path.exists(BaseGenerator.BUILD_DIR):
            os.makedirs(BaseGenerator.BUILD_DIR)

        self.jinja2_environment = Environment(loader=PackageLoader(__name__, "templates/{}/".format(self.templates)),
                                              extensions=['jinja2.ext.with_'],
                                              trim_blocks=True,
                                              lstrip_blocks=True)

    def process(self):
        if self.core_data_path is not None:
            if self.is_xcode_running():
                raise SignalsError("Must quit Xcode before writing to core data")
            progress("Creating core data file")
            write_xml_to_file(self.core_data_path, self.schema.data_objects)

        if self.template_options[self.templates] == self.template_options['objc']:
            print 'Preparing to generate Objective-C templates...'
            template_to_generate = ObjectiveCTemplate(self.project_name,
                                                      self.schema,
                                                      self.data_models_path,
                                                      self.jinja2_environment,
                                                      BaseGenerator.BUILD_DIR)
        else:
            # Swift code goes here
            print 'Preparing to generate Swift templates...'
            template_to_generate = SwiftTemplate(self.project_name,
                                                 self.schema,
                                                 self.data_models_path,
                                                 self.jinja2_environment,
                                                 BaseGenerator.BUILD_DIR)

        progress("Creating data model file")

        template_to_generate.process()

        self.check_setup_called()

    def check_setup_called(self):
        # Find parent path that contains AppDelegate.swift
        parent_path_containing_target, filename = recursively_find_parent_containing_file(self.data_models_path,
                                                                                          ["AppDelegate.swift",
                                                                                           "AppDelegate.m"])
        if parent_path_containing_target is None:
            warn("Warning: Unable to find AppDelegate.swift or AppDelegate.m to verify "
                 "sharedDataModel().setup() is called")
            return False

        # Walk the file looking for setup call
        with open(parent_path_containing_target + os.sep + filename) as f:
            for line in f:
                # Looking for either the objective-c version or the swift version of the setup call.
                # Assuming roughly the following format:
                # Objective-c: [[DataModel sharedDataModel] setup]
                # Swift:       DataModel.sharedDataModel().setup()
                data_model_index = line.find("DataModel")
                shared_data_model_index = line.find("sharedDataModel")
                setup_index = line.find("setup")
                if 0 <= data_model_index and \
                   data_model_index < shared_data_model_index and \
                   shared_data_model_index < setup_index:
                    return True

        warn("Warning: Did not find sharedDataModel().setup() call inside AppDelegate.swift")
        return False

    @staticmethod
    def is_xcode_running():
        return "Xcode.app" in subprocess.check_output(["ps", "-Ax"])
