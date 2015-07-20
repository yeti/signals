from datetime import date
import os
import re
from yak_signals.generators.base.base_generator import BaseGenerator
from yak_signals.parser.fields import Field, Relationship
from yak_signals.parser.api import PatchAPI, GetAPI, API

DATA_TYPES = {
    Field.DATE: "NSDate*",
    Field.DATETIME: "NSDate*",
    Field.INTEGER: "NSNumber*",
    Field.DECIMAL: "NSNumber*",
    Field.FLOAT: "NSNumber*",
    Field.STRING: "NSString*",
    Field.TEXT: "NSString*",
    Field.BOOLEAN: "NSNumber*",
    Field.IMAGE: "UIImage*",
    Field.VIDEO: "NSURL*"
}

def get_objc_data_type(field_type):
    if field_type == Field.ARRAY:
        return "NSArray*"
    else:
        return DATA_TYPES[field_type]


def create_header(file, file_name):
    template = """
//
//  {}
//
//  Created by Manticom on {}.
//  Copyright (c) {} Yeti. All rights reserved.
//
"""
    today = date.today()
    file.write(template.format(file_name, today, today.year))


def create_header_for_h_file(h):
    create_header(h, "DataModel.h")

    template = """
#import <Foundation/Foundation.h>

@class RKObjectRequestOperation;
@class RKMappingResult;
@class UIImage;

@interface DataModel : NSObject

+ (DataModel *)sharedDataModel;

"""
    today = date.today()
    h.write(template.format(today, today.year))


def create_header_for_m_file(m):
    create_header(m, "DataModel.m")


def create_footer_for_h_file(h):
    template = """
- (void)setup;

@end
"""
    h.write(template)


def write_doc_string(h_file, url, api):
    template = """/**

{}

*/
"""

    def format_doc(documentation):
        return "\t{}".format(documentation)

    # Try to find a doc string to print in the main API object or in the specific method call
    doc_strings = []
    if url.documentation:
        doc_strings.append(format_doc(url.documentation))

    if api.documentation:
        doc_strings.append(format_doc(api.documentation))

    if len(doc_strings) > 0:
        h_file.write(template.format("\n\n".join(doc_strings)))


# TODO: try to combine this with sanitize api name
def create_descriptor_name(api):
    sanitized_name = ""
    for part in re.split(r'[/_]+', api):
        if part in [":id", "theID"]:
            sanitized_name += "WithId"
        else:
            sanitized_name += part.capitalize()

    return sanitized_name[0].lower() + sanitized_name[1:]


def sanitize_api_name(api):
    sanitized_name = ""
    for part in re.split(r'[/_]+', api):
        if part in [":id", "theID"]:
            continue
        else:
            sanitized_name += part.capitalize()

    return sanitized_name


def check_for_id(api):
    return ':id' in api


def check_and_write_for_id(h, url):
    if check_for_id(url):
        url = url.replace(":id", "%@")
        h.write('    NSString* formattedUrl = [NSString stringWithFormat:@"{}", theID];\n'.format(url))
        return 'formattedUrl'
    else:
        return '@"{}"'.format(url)


def write_login_to_files(h_file, m_file):
    h_file.write('- (void) getAllLoginWithUsername:(NSString*)username password:(NSString*)password success:(void (^)(RKObjectRequestOperation *operation, RKMappingResult *mappingResult))success failure:(void (^)(RKObjectRequestOperation *operation, NSError *error))failure {\n')
    h_file.write('   RKObjectManager* sharedMgr = [RKObjectManager sharedManager];\n')
    h_file.write('   [sharedMgr.HTTPClient setAuthorizationHeaderWithUsername:username password:password];\n')
    h_file.write('   sharedMgr.requestSerializationMIMEType = RKMIMETypeFormURLEncoded;\n')
    h_file.write('   [sharedMgr getObjectsAtPath:@"login/" parameters:nil success:success failure:failure];\n')
    h_file.write('}\n')

    m_file.write('- (void) getAllLoginWithUsername:(NSString*)username password:(NSString*)password success:(void (^)(RKObjectRequestOperation *operation, RKMappingResult *mappingResult))success failure:(void (^)(RKObjectRequestOperation *operation, NSError *error))failure;\n')


def write_get_calls_to_files(url, api, h_file, m_file):
    write_doc_string(m_file, url, api)

    has_id = check_for_id(url.url_path)
    if has_id:
        method_snippet = "WithID:(NSNumber*)theID  andSuccess:"
    else:
        method_snippet = "WithSuccess:"

    name = sanitize_api_name(url.url_path)
    method_signature = '- (void) get{}{}(void (^)(RKObjectRequestOperation *operation, RKMappingResult *result))success failure:(void (^)(RKObjectRequestOperation *operation, NSError *error))failure'.format(name, method_snippet)
    h_file.write("{} {{\n".format(method_signature))
    write_shared_manager(h_file)
    write_authentication(h_file, api)
    write_content_type(h_file, api.content_type)
    endpoint = check_and_write_for_id(h_file, url.url_path)
    h_file.write('    [sharedMgr getObjectsAtPath:{} parameters:nil success:success failure:failure];\n'.format(endpoint))
    h_file.write('}\n\n')

    m_file.write("{};\n\n".format(method_signature))


def create_request_descriptor(h, api):
    object_name = get_object_name(api.request_object)
    descriptor_name = '{}{}RequestDescriptor'.format(create_descriptor_name(api.url_path), api.method.capitalize())
    mapping_name = get_mapping_name(api.request_object)

    # If this is a patch, we need to set `assignsDefaultValueForMissingAttributes`
    inverse_mapping = "[{} inverseMapping]".format(mapping_name)
    if isinstance(api, PatchAPI):
        inverse_mapping = "{}Inverse".format(mapping_name)
        h.write('RKEntityMapping *{} = [{} inverseMapping];\n'.format(inverse_mapping, mapping_name))
        h.write('{}.assignsDefaultValueForMissingAttributes = NO;\n'.format(inverse_mapping))

    h.write('RKRequestDescriptor *{} = [RKRequestDescriptor requestDescriptorWithMapping:{} objectClass:[{} class] rootKeyPath:nil method:RKRequestMethod{}];\n'.format(descriptor_name, inverse_mapping, object_name, api.method.upper()))
    h.write('[objectManager addRequestDescriptor:{}];\n'.format(descriptor_name))
    h.write('\n')


def create_response_descriptor(h, api):
    descriptor_name = '{}{}ResponseDescriptor'.format(create_descriptor_name(api.url_path), api.method.capitalize())
    mapping_name = get_mapping_name(api.response_object)

    key_path = 'nil'
    if hasattr(api, 'resource_type'):
        key_path = 'nil' if api.resource_type == GetAPI.RESOURCE_DETAIL else '@"results"'
    elif isinstance(api, GetAPI) and ':id' not in api.url_path:
        # Get requests with an ID only return 1 object, not a list of results
        key_path = '@"results"'

    h.write('RKResponseDescriptor *{} = [RKResponseDescriptor responseDescriptorWithMapping:{} method:RKRequestMethod{} pathPattern:@"{}" keyPath:{} statusCodes:RKStatusCodeIndexSetForClass(RKStatusCodeClassSuccessful)];\n'.format(descriptor_name, mapping_name, api.method.upper(), api.url_path, key_path))
    h.write('[objectManager addResponseDescriptor:{}];\n'.format(descriptor_name))
    h.write('\n')


def get_mapping_name(obj):
    return "{}{}Mapping".format(obj[1].lower(), obj[2:])


def get_object_name(obj):
    return obj[1].upper() + obj[2:]


def get_parameter_variable_name(parameter):
    parameter_variable_name = parameter
    if "__" in parameter:
        parameter_names = parameter.split('__')
        parameter_variable_name = parameter_names[1] + parameter_names[0].capitalize()
    elif "_" in parameter:
        parameter_names = parameter.split('_')
        parameter_variable_name = parameter_names[1]
    return parameter_variable_name


def write_shared_manager(h):
    h.write('    RKObjectManager* sharedMgr = [RKObjectManager sharedManager];\n')


def write_authentication(h, api):
    if api.authorization == API.OAUTH2 and not api.authorization_optional:
        h.write('    [sharedMgr.HTTPClient setDefaultHeader:@"Authorization" value:[NSString stringWithFormat:@"Bearer %@", [AppModel sharedModel].accessToken]];\n')


def write_content_type(h, content_type):
    if content_type == API.CONTENT_TYPE_JSON:
        h.write('    sharedMgr.requestSerializationMIMEType = RKMIMETypeJSON;\n')
    elif content_type == API.CONTENT_TYPE_FORM:
        h.write('    sharedMgr.requestSerializationMIMEType = RKMIMETypeFormURLEncoded;\n')


# Changes a python variable name to an objective c version
# ex. access_token_secret -> accessTokenSecret
def python_to_objc_variable(python_variable_name):
    words = python_variable_name.split('_')
    return words[0] + "".join(word.capitalize() for word in words[1:])


# id and description are reserved words in Objective C so we'll replace them with our own
def sanitize_field_name(field_name):
    if field_name == "id":
        return "theID"
    elif field_name == "description":
        return "theDescription"
    else:
        return field_name


def assign_fields(m, request_object):
    for field in request_object.properties():
        # Don't assign images or videos to the object
        if field.field_type in [Field.IMAGE, Field.VIDEO]:
            continue

        obj_variable = sanitize_field_name(field.name)
        obj_variable = python_to_objc_variable(obj_variable)
        m.write('    obj.{0} = {0};\n'.format(obj_variable))


def build_method_signature(name, variable_type, capitalize=False):
    field_name = sanitize_field_name(name)
    variable_name = python_to_objc_variable(field_name)

    # The tag name is only capitalized if it's part of the method name, when it's the first field
    tag_name = variable_name[0].upper() + variable_name[1:] if capitalize else variable_name

    return "{0}:({1}){2} ".format(tag_name, variable_type, variable_name)


def write_method_signature(h, m, request_object, url, api):
    method_title = sanitize_api_name(url.url_path)
    method_signature = '- (void) {}{}With'.format(api.method, method_title)

    has_id = False
    if request_object is not None:
        # Create all of the parameters based on the request object's fields
        for index, field in enumerate(request_object.fields):
            if field.name == 'id':
                has_id = True

            variable_type = get_objc_data_type(field.field_type)
            method_signature += build_method_signature(field.name, variable_type, index == 0)

        for relationship in request_object.relationships:
            if relationship.relationship_type in [Relationship.MANY_TO_MANY, Relationship.ONE_TO_MANY]:
                variable_type = 'NSOrderedSet*'
            else:
                variable_type = get_object_name(relationship.related_object)
            method_signature += build_method_signature(relationship.name, variable_type, True)

    # Also add an ID parameter if we need an ID for the url and it's not already a field on our object
    if "id" in url.url_path and not has_id:
        method_signature += "theID:(NSNumber*)theID "

    method_signature_end = ":(void (^)(RKObjectRequestOperation *operation, RKMappingResult *mappingResult))success failure:(void (^)(RKObjectRequestOperation *operation, NSError *error))failure"
    if request_object is None or len(request_object.properties()) == 0:
        method_signature = "{}Success{}".format(method_signature, method_signature_end)
    else:
        method_signature = "{} success{}".format(method_signature[:-1], method_signature_end)

    h.write("{} {{\n".format(method_signature))

    write_doc_string(m, url, api)
    m.write("{};\n\n".format(method_signature))


def write_api_call(m, path, api, request_object):
    obj_variable_name = "obj" if request_object else "nil"
    json_api_call = '[sharedMgr {}Object:{} path:{} parameters:nil success:success failure:failure];'.format(api.method,
                                                                                                             obj_variable_name,
                                                                                                             path)

    media_fields = []
    if request_object is not None:
        # If we have any videos or images, we'll need to make a multipart form request
        media_fields = filter(lambda field: field.field_type in [Field.IMAGE, Field.VIDEO], request_object.fields)
    if len(media_fields) > 0:

        multipart_upload_template = """
    if ({}) {{
        NSMutableURLRequest *request = [sharedMgr multipartFormRequestWithObject:obj method:RKRequestMethod{} path:{} parameters:nil
                                                       constructingBodyWithBlock:^(id<AFMultipartFormData> formData) {{
                                                           {}
                                                       }}];
        RKManagedObjectRequestOperation *operation = [sharedMgr managedObjectRequestOperationWithRequest:request managedObjectContext:nil success:success failure:failure];
        [sharedMgr enqueueObjectRequestOperation:operation];
    }} else {{
        {}
    }}
"""

        variable_conditional = " || ".join("{} != nil".format(python_to_objc_variable(field.name)) for field in media_fields)

        appended_files = ""
        for field in media_fields:
            if field.field_type == 'image':
                image_upload_template = """                [formData appendPartWithFileData:UIImageJPEGRepresentation({0}, 1)
                                                                                       name:@"{1}"
                                                                                   fileName:@"{1}.jpeg"
                                                                                   mimeType:@"image/jpeg"];
"""
                appended_files += image_upload_template.format(python_to_objc_variable(field.name), field.name)
            elif field.field_type == 'video':
                appended_files += '[formData appendPartWithFileURL:{0} name:@"{1}" fileName:@"{1}.mp4" mimeType:@"video/mp4" error:nil];\n'.format(python_to_objc_variable(field.name), field.name)

        m.write(multipart_upload_template.format(variable_conditional, api.method.upper(), path, appended_files,
                                                 json_api_call))
    else:
        # else we can just use RestKit's normal JSON API call
        m.write('  {}\n'.format(json_api_call))


def create_mappings(urls, data_objects, project_name):
    if not os.path.exists(BaseGenerator.BUILD_DIR):
        os.makedirs(BaseGenerator.BUILD_DIR)

    # TODO: these are named backwards
    implementation_file_path = "{}/MachineDataModel.m".format(BaseGenerator.BUILD_DIR)
    header_file_path = "{}/MachineDataModel.h".format(BaseGenerator.BUILD_DIR)
    with open(implementation_file_path, "w") as h, open(header_file_path, 'w') as m:
        create_header_for_h_file(m)
        create_header_for_m_file(h)

        # First, write imports in DataModel.m
        h.write('\n')
        h.write('#import "DataModel.h"\n')
        h.write('#import <CoreData/CoreData.h>\n')
        h.write('#import <RestKit/RestKit.h>\n')
        h.write('#import "{}-Swift.h"\n'.format(project_name))

        # TODO: ideally we don't loop over objects twice, but easiest for now due to order of writing into .m file
        for object_name, data_object in data_objects.iteritems():
            if "Request" in object_name:
                request_variable = get_object_name(object_name)
                h.write('#import "{}.h"\n'.format(request_variable))
        h.write('\n')

        # Setup Mappings
        property_mappings = {}
        for object_name, data_object in data_objects.iteritems():
            if "Parameters" not in object_name:
                mapping_name = get_mapping_name(object_name)
                proper_object_name = get_object_name(object_name)
                h.write('RKEntityMapping *{} = [RKEntityMapping mappingForEntityForName:@"{}" inManagedObjectStore:managedObjectStore];\n'.format(mapping_name, proper_object_name))

                attributes = []
                properties = []
                for field in data_object.fields:
                    if field.primary_key:
                        primary_key = field.name
                        if primary_key == 'id':
                            primary_key = 'theID'
                        h.write('{}.identificationAttributes = @[@"{}"];\n'.format(mapping_name, primary_key))

                    # don't create attributes for files
                    if field.field_type not in ["video", "image"]:
                        attributes.append(field.name)

                for relationship in data_object.relationships:
                    properties.append((relationship.name, relationship.related_object))

                # Setup Attributes
                if len(attributes) > 0:
                    attribute_mappings = '[{} addAttributeMappingsFromDictionary:@{{'.format(mapping_name)
                    for attribute in attributes:
                        field_name = sanitize_field_name(attribute)
                        if '_' in attribute:
                            words = field_name.split('_')
                            field_name = words[0]
                            for x in range(1, len(words)):
                                field_name += words[x].capitalize()

                        attribute_mappings += '@"{}": @"{}", '.format(attribute, field_name)
                    # remove last comma and space then close the statement
                    attribute_mappings = attribute_mappings[:-2] + '}];\n'
                    h.write(attribute_mappings)
                h.write('\n')

                property_mappings[mapping_name] = properties

        h.write("// Add all related mappings after we've created all the objects so we don't worry about ordering\n")
        for proper_object_name, properties in property_mappings.iteritems():
            if len(properties) > 0:
                for property_name, related_object_name in properties:
                    mapping_name = get_mapping_name(related_object_name)
                    h.write('[{0} addPropertyMapping:[RKRelationshipMapping relationshipMappingFromKeyPath:@"{1}" toKeyPath:@"{1}" withMapping:{2}]];\n'.format(proper_object_name, property_name, mapping_name))
        h.write('\n')

        # Create restkit request and response descriptors
        for url in urls:
            # Delete's don't need descriptors
            if url.patch:
                create_request_descriptor(h, url.patch)
                create_response_descriptor(h, url.patch)

            if url.get:
                create_response_descriptor(h, url.get)

            if url.post:
                create_request_descriptor(h, url.post)
                create_response_descriptor(h, url.post)
        h.write('\n')

        # Get requests with no ID's, ID's and no Parameters"
        for url in urls:
            if url.get:
                write_get_calls_to_files(url, url.get, h, m)
        h.write('\n')
        
        # Create the rest of our API endpoints
        for url in urls:
            if url.get and url.get.parameters_object:
                api = url.get
                if url.url_path != "login/":
                    parameters_object = data_objects[api.parameters_object]
                    write_doc_string(m, url, api)

                    title = '- (void) get{}With'.format(sanitize_api_name(url.url_path))
                    for field in parameters_object.fields:
                        parameter_variable_name = get_parameter_variable_name(field.name)
                        title += "{}:({}){} ".format(parameter_variable_name.capitalize(),
                                                     get_objc_data_type(field.field_type),
                                                     parameter_variable_name)

                    success_failure_params = "success:(void (^)(RKObjectRequestOperation *operation, RKMappingResult *result))success failure:(void (^)(RKObjectRequestOperation *operation, NSError *error))failure"

                    h.write("{}{} {{\n".format(title, success_failure_params))
                    m.write("{}{};\n\n".format(title, success_failure_params))
                    h.write("    NSMutableDictionary* queryParams = [NSMutableDictionary dictionaryWithCapacity:{}];\n".format(len(parameters_object.fields)))

                    for field in parameters_object.fields:
                        parameter_variable_name = get_parameter_variable_name(field.name)
                        h.write("    if ({}) {{\n".format(parameter_variable_name))
                        h.write('      [queryParams setObject:{} forKey:@"{}"];\n'.format(parameter_variable_name, field.name))
                        h.write("    }\n")

                    write_shared_manager(h)
                    write_content_type(h, api.content_type)
                    h.write('    [sharedMgr getObjectsAtPath:@"{}" parameters:queryParams success:success failure:failure];\n'.format(url.url_path))
                    h.write('}\n\n')

            if url.post:
                api = url.post
                request_object = data_objects[api.request_object]

                write_method_signature(h, m, request_object, url, api)

                write_shared_manager(h)
                request_variable = api.request_object[1].capitalize() + api.request_object[2:]
                h.write('    {0} *obj = [NSEntityDescription insertNewObjectForEntityForName:@"{0}" inManagedObjectContext:sharedMgr.managedObjectStore.mainQueueManagedObjectContext];\n'.format(request_variable))

                assign_fields(h, request_object)
                path = check_and_write_for_id(h, url.url_path)
                write_authentication(h, api)
                write_content_type(h, api.content_type)
                write_api_call(h, path, api, request_object)

                h.write('}\n\n')

            if url.patch:
                if "id" in url.url_path:
                    api = url.patch
                    request_object = data_objects[api.request_object]

                    write_method_signature(h, m, request_object, url, api)

                    write_shared_manager(h)
                    request_variable = api.request_object[1].capitalize() + api.request_object[2:]
                    h.write('    {0} *obj = [NSEntityDescription insertNewObjectForEntityForName:@"{0}" inManagedObjectContext:sharedMgr.managedObjectStore.mainQueueManagedObjectContext];\n'.format(request_variable))

                    assign_fields(h, request_object)
                    write_authentication(h, api)
                    write_content_type(h, api.content_type)
                    path = check_and_write_for_id(h, url.url_path)
                    write_api_call(h, path, api, request_object)

                    h.write('}\n\n')

            # DELETE
            if url.delete:
                if "id" in url.url_path:
                    api = url.delete
                    write_method_signature(h, m, None, url, api)
                    write_shared_manager(h)
                    write_authentication(h, api)
                    write_content_type(h, api.content_type)
                    path = check_and_write_for_id(h, url.url_path)
                    write_api_call(h, path, api, None)
                    h.write('}\n\n')
        
        # LOGIN
        write_login_to_files(h, m)

        create_footer_for_h_file(m)
