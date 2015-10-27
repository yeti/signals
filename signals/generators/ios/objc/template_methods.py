from signals.generators.ios.conversion import get_proper_name
from signals.generators.ios.ios_template_methods import iOSTemplateMethods
from signals.generators.ios.objc.parameters import ObjCParameter
from signals.parser.api import GetAPI


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
