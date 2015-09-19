from datetime import datetime
from inspect import getmembers, isfunction
import os
from signals.helpers import recursively_find_parent_containing_file
import subprocess
from jinja2 import Environment, PackageLoader
import shutil
from signals.logging import SignalsError, progress, warn
from signals.generators.ios.conversion import sanitize_field_name
from signals.parser.fields import Field
from signals.parser.schema import URL
from signals.generators.base.base_generator import BaseGenerator
from signals.generators.ios.core_data import write_xml_to_file
from signals.generators.ios import template_methods


class iOSGenerator(BaseGenerator):
    def __init__(self, schema, data_models_path, core_data_path, project_name):
        super(iOSGenerator, self).__init__(schema)
        # Command flags
        self.data_models_path = data_models_path
        self.core_data_path = core_data_path
        self.project_name = project_name

        # Setup
        if not os.path.exists(BaseGenerator.BUILD_DIR):
            os.makedirs(BaseGenerator.BUILD_DIR)
        self.header_file = "{}/{}DataModel.h".format(BaseGenerator.BUILD_DIR, self.project_name)
        self.implementation_file = "{}/{}DataModel.m".format(BaseGenerator.BUILD_DIR, self.project_name)
        self.jinja2_environment = Environment(loader=PackageLoader(__name__),
                                              extensions=['jinja2.ext.with_'],
                                              trim_blocks=True,
                                              lstrip_blocks=True)

    def process(self):
        if self.core_data_path is not None:
            if self.is_xcode_running():
                raise SignalsError("Must quit Xcode before writing to core data")
            progress("Creating core data file")
            write_xml_to_file(self.core_data_path, self.schema.data_objects)

        progress("Creating data model file")
        self.create_header_file()
        self.create_implementation_file()
        self.copy_data_models()
        self.check_setup_called()

    def create_header_file(self):
        self.process_template('data_model.h.j2', self.header_file, {})

    def create_implementation_file(self):
        self.process_template('data_model.m.j2', self.implementation_file, {
            'project_name': self.project_name,
            'VIDEO_FIELD': Field.VIDEO,
            'IMAGE_FIELD': Field.IMAGE,
            'request_objects': self.get_request_objects(self.schema.data_objects),
            'sanitize_field_name': sanitize_field_name
        })

    def process_template(self, template_name, template_file_path, extra_context):
        template = self.jinja2_environment.get_template(template_name)
        context = {
            'today': datetime.today(),
            'endpoints': URL.URL_ENDPOINTS.keys(),
            'schema': self.schema,
        }
        context.update(extra_context)
        # Registers all methods in template_methods.py with jinja2 for use
        context.update({name: method for name, method in getmembers(template_methods, isfunction)})
        template_output = template.render(**context)
        with open(template_file_path, "w") as output_file:
            output_file.write(template_output)

    def copy_data_models(self):
        shutil.copyfile(self.header_file, "{}/DataModel.h".format(self.data_models_path))
        shutil.copyfile(self.implementation_file, "{}/DataModel.m".format(self.data_models_path))

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

    @staticmethod
    def get_request_objects(data_objects):
        request_objects = []
        for name, data_object in data_objects.iteritems():
            # TODO: Naming request objects as ...Request is not a standard we always keep true
            if 'Request' in name:
                request_objects.append(data_object)
        return request_objects
