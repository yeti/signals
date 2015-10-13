import shutil
from signals.generators.base.base_template import BaseTemplate
from signals.generators.ios.conversion import sanitize_field_name, get_proper_name
from signals.generators.ios.parameters import ObjCParameter
from signals.generators.ios.ios_template_methods import iOSTemplateMethods
from signals.parser.api import GetAPI
from signals.parser.fields import Field


class ObjectiveCTemplate(BaseTemplate):
    def __init__(self, project_name, schema, data_models_path, jinja2_environment, build_dir):
        super(ObjectiveCTemplate, self).__init__(project_name, schema, data_models_path, jinja2_environment)
        # File Paths
        self.header_file = "{}/{}DataModel.h".format(build_dir, project_name)
        self.implementation_file = "{}/{}DataModel.m".format(build_dir, project_name)

    def process(self):
        self.create_header_file()
        self.create_implementation_file()
        self.copy_data_models()

    def create_header_file(self):
        self.process_template('data_model.h.j2', self.header_file, ObjectiveCTemplateMethods, {})

    def create_implementation_file(self):
        self.process_template('data_model.m.j2', self.implementation_file, ObjectiveCTemplateMethods, {
            'project_name': self.project_name,
            'VIDEO_FIELD': Field.VIDEO,
            'IMAGE_FIELD': Field.IMAGE,
            'get_proper_name': get_proper_name,
            'request_objects': self.get_request_objects(self.schema.data_objects),
            'sanitize_field_name': sanitize_field_name
        })

    def copy_data_models(self):
        shutil.copyfile(self.header_file, "{}/DataModel.h".format(self.data_models_path))
        shutil.copyfile(self.implementation_file, "{}/DataModel.m".format(self.data_models_path))


class ObjectiveCTemplateMethods(iOSTemplateMethods):
    @staticmethod
    def method_parameters(api):
        parameters = []

        # Create request object parameters
        request_object = iOSTemplateMethods.get_api_request_object(api)
        if request_object:
            parameters.extend(ObjCParameter.generate_field_parameters(request_object))
            parameters.extend(ObjCParameter.generate_relationship_parameters(request_object))

        # Add id parameter if we need it
        id_parameter = ObjCParameter.create_id_parameter(api.url_path, request_object)
        if id_parameter:
            parameters.append(id_parameter)

        # Add required RestKit parameters
        parameters.extend([
            ObjCParameter(name="success",
                          objc_type="void (^)(RKObjectRequestOperation *operation, RKMappingResult *mappingResult)"),
            ObjCParameter(name="failure",
                          objc_type="void (^)(RKObjectRequestOperation *operation, NSError *error)")
        ])

        return ObjectiveCTemplateMethods.create_parameter_signature(parameters)

    @staticmethod
    def key_path(api):
        key_path_string = 'nil'
        if hasattr(api, 'resource_type'):
            key_path_string = 'nil' if api.resource_type == GetAPI.RESOURCE_DETAIL else '@"results"'
        elif isinstance(api, GetAPI) and ':id' not in api.url_path:
            # Get requests with an ID only return 1 object, not a list of results
            key_path_string = '@"results"'
        return key_path_string

    @staticmethod
    def attribute_mappings(fields):
        attribute_mapping_string = ""
        for index, field in enumerate(fields):
            leading_comma = '' if index == 0 else ', '
            objc_variable_name = get_proper_name(field.name)
            attribute_mapping_string += '{}@"{}": @"{}"'.format(leading_comma, field.name, objc_variable_name)
        return attribute_mapping_string

    @staticmethod
    def create_parameter_signature(parameters):
        method_parts = []
        for index, method_field in enumerate(parameters):
            objc_variable_name = get_proper_name(method_field.name)
            parameter_signature = "({}){}".format(method_field.objc_type, objc_variable_name)
            # If this isn't the first parameter, also include the variable name before the type
            if index > 0:
                parameter_signature = "{}:{}".format(objc_variable_name, parameter_signature)

            method_parts.append(parameter_signature)

        return " ".join(method_parts)
