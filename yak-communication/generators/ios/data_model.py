from datetime import date
import re

OBJC_DATA_TYPES = {
    "date"       : "NSDate*",
    "datetime"   : "NSDate*",
    "int"        : "NSNumber*",
    "integer"    : "NSNumber*",
    "integer16"  : "NSNumber*",
    "integer32"  : "NSNumber*",
    "integer64"  : "NSNumber*",
    "decimal"    : "NSNumber*",
    "double"     : "NSNumber*",
    "real"       : "NSNumber*",
    "float"      : "NSNumber*",
    "string"     : "NSString*",
    "text"       : "NSString*",
    "boolean"    : "NSNumber*",
    "array"      : "NSArray*",
    "list"       : "NSArray*",
    "video"      : "NSURL*",
    "image"      : "UIImage*"
}


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


def write_doc_string(h_file, url, method):
    template = """/**

{}

*/
"""

    def format_doc(doc):
        return "\t{}".format(doc)

    # Try to find a doc string to print in the main API object or in the specific method call
    doc_strings = []
    if 'doc' in url:
        doc_strings.append(format_doc(url['doc']))

    if 'doc' in url[method]:
        doc_strings.append(format_doc(url[method]['doc']))

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


def write_get_calls_to_files(url, h_file, m_file):
    write_doc_string(m_file, url, 'get')

    has_id = check_for_id(url["url"])
    if has_id:
        method_snippet = "WithID:(NSNumber*)theID  andSuccess:"
    else:
        method_snippet = "WithSuccess:"

    name = sanitize_api_name(url["url"])
    method_signature = '- (void) get{}{}(void (^)(RKObjectRequestOperation *operation, RKMappingResult *result))success failure:(void (^)(RKObjectRequestOperation *operation, NSError *error))failure'.format(name, method_snippet)
    h_file.write("{} {{\n".format(method_signature))
    write_shared_manager(h_file)
    write_authentication(h_file, url['get']['#meta'])
    write_content_type(h_file, url['get'].get('content_type', 'json'))
    api = check_and_write_for_id(h_file, url["url"])
    h_file.write('    [sharedMgr getObjectsAtPath:{} parameters:nil success:success failure:failure];\n'.format(api))
    h_file.write('}\n\n')

    m_file.write("{};\n\n".format(method_signature))


def create_request_descriptor(h, url, method):
    info = url[method]
    object_variable_name = info['request']
    object_name = get_object_name(object_variable_name)
    descriptor_name = '{}{}RequestDescriptor'.format(create_descriptor_name(url['url']), method.capitalize())
    mapping_name = get_mapping_name(object_variable_name)

    # If this is a patch, we need to set `assignsDefaultValueForMissingAttributes`
    inverse_mapping = "[{} inverseMapping]".format(mapping_name)
    if method == "patch":
        inverse_mapping = "{}Inverse".format(mapping_name)
        h.write('RKEntityMapping *{} = [{} inverseMapping];\n'.format(inverse_mapping, mapping_name))
        h.write('{}.assignsDefaultValueForMissingAttributes = NO;\n'.format(inverse_mapping))

    h.write('RKRequestDescriptor *{} = [RKRequestDescriptor requestDescriptorWithMapping:{} objectClass:[{} class] rootKeyPath:nil method:RKRequestMethod{}];\n'.format(descriptor_name, inverse_mapping, object_name, method.upper()))
    h.write('[objectManager addRequestDescriptor:{}];\n'.format(descriptor_name))
    h.write('\n')


def create_response_descriptor(h, url, method):
    info = url[method]
    object_variable_name = info['response']['200+']
    descriptor_name = '{}{}ResponseDescriptor'.format(create_descriptor_name(url['url']), method.capitalize())
    mapping_name = get_mapping_name(object_variable_name)

    key_path = 'nil'
    if 'resource_type' in info:
        key_path = 'nil' if info['resource_type'] == 'detail' else '@"results"'
    elif method == "get" and ':id' not in url['url']:
        # Get requests with an ID only return 1 object, not a list of results
        key_path = '@"results"'

    h.write('RKResponseDescriptor *{} = [RKResponseDescriptor responseDescriptorWithMapping:{} method:RKRequestMethod{} pathPattern:@"{}" keyPath:{} statusCodes:RKStatusCodeIndexSetForClass(RKStatusCodeClassSuccessful)];\n'.format(descriptor_name, mapping_name, method.upper(), url['url'], key_path))
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


def write_authentication(h, meta):
    # TODO: What to do about optional auth?
    if 'oauth2' in meta and 'optional' not in meta:
        h.write('    [sharedMgr.HTTPClient setDefaultHeader:@"Authorization" value:[NSString stringWithFormat:@"Bearer %@", [AppModel sharedModel].accessToken]];\n')


def write_content_type(h, content_type):
    if content_type == 'json':
        h.write('    sharedMgr.requestSerializationMIMEType = RKMIMETypeJSON;\n')
    elif content_type == 'form':
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
    for field_name, values in request_object.iteritems():
        # Don't assign images or videos to the object
        if 'image' in values or 'video' in values:
            continue

        obj_variable = sanitize_field_name(field_name)
        obj_variable = python_to_objc_variable(obj_variable)
        m.write('    obj.{0} = {0};\n'.format(obj_variable))


def write_method_signature(h, m, request_object, url, method_type):
    method_title = sanitize_api_name(url['url'])
    method_signature = '- (void) {}{}With'.format(method_type, method_title)

    # Create all of the parameters based on the request object's fields
    for index, (field_name, field_values) in enumerate(request_object.iteritems()):
        field_name = sanitize_field_name(field_name)
        variable_name = python_to_objc_variable(field_name)

        # TODO: this depends on the type (i.e. int or string) being the first value
        # changes schema value to Objective C variable type (i.e. image -> UIImage)
        variable_type = OBJC_DATA_TYPES[field_values.split(',')[0]]

        # The tag name is only capitalized if it's part of the method name, when it's the first field
        tag_name = variable_name[0].upper() + variable_name[1:] if index == 0 else variable_name

        method_signature += "{0}:({1}){2} ".format(tag_name, variable_type, variable_name)

    # Also add an ID parameter if we need an ID for the url and it's not already a field on our object
    if "id" in url['url'] and 'id' not in request_object:
        method_signature += "theID:(NSNumber*)theID "

    method_signature = method_signature[:-1] + " success:(void (^)(RKObjectRequestOperation *operation, RKMappingResult *mappingResult))success failure:(void (^)(RKObjectRequestOperation *operation, NSError *error))failure"

    h.write("{} {{\n".format(method_signature))

    write_doc_string(m, url, method_type)
    m.write("{};\n\n".format(method_signature))


def write_api_call(m, path, method, request_object):
    obj_variable_name = "obj" if request_object else "nil"
    json_api_call = '[sharedMgr {}Object:{} path:{} parameters:nil success:success failure:failure];'.format(method,
                                                                                                             obj_variable_name,
                                                                                                             path)

    # If we have any videos or images, we'll need to make a multipart form request
    media_fields = filter(lambda (_, values): 'image' in values or 'video' in values, request_object.items())
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

        variable_conditional = " || ".join("{} != nil".format(python_to_objc_variable(field_name)) for (field_name, _) in media_fields)

        appended_files = ""
        for field_name, values in media_fields:
            if 'image' in values:
                image_upload_template = """                [formData appendPartWithFileData:UIImageJPEGRepresentation({0}, 1)
                                                                                       name:@"{1}"
                                                                                   fileName:@"{1}.jpeg"
                                                                                   mimeType:@"image/jpeg"];
"""
                appended_files += image_upload_template.format(python_to_objc_variable(field_name), field_name)
            elif 'video' in values:
                appended_files += '[formData appendPartWithFileURL:{0} name:@"{1}" fileName:@"{1}.mp4" mimeType:@"video/mp4" error:nil];\n'.format(python_to_objc_variable(field_name), field_name)

        m.write(multipart_upload_template.format(variable_conditional, method.upper(), path, appended_files, json_api_call))
    else:
        # else we can just use RestKit's normal JSON API call
        m.write('  {}\n'.format(json_api_call))


def create_mappings(urls, objects):
    # TODO: Rename and clean these globals up
    params = {}
    requests = {}

    # Mappings
    # TODO: these are named backwards
    with open("MachineDataModel.m", "w") as h, open("MachineDataModel.h", 'w') as m:
        create_header_for_h_file(m)
        create_header_for_m_file(h)

        # First, write imports in DataModel.m
        h.write('\n')
        h.write('#import "DataModel.h"\n')
        h.write('#import <CoreData/CoreData.h>\n')
        h.write('#import <RestKit/RestKit.h>\n')
        h.write('#import "Viddit-Swift.h"\n')

        # TODO: ideally we don't loop over objects twice, but easiest for now due to order of writing into .m file
        for obj in objects:
            # ex. $userRequest
            obj_variable_name = obj.keys()[0]

            if "Request" in obj_variable_name:
                requests[obj_variable_name] = obj
                request_variable = get_object_name(obj_variable_name)
                h.write('#import "{}.h"\n'.format(request_variable))
        h.write('\n')

        # Setup Mappings
        property_mappings = {}
        for obj in objects:
            # ex. $userRequest
            obj_variable_name = obj.keys()[0]
            params[obj_variable_name] = obj[obj_variable_name]

            if "Parameters" not in obj_variable_name:
                name = get_mapping_name(obj_variable_name)
                obj_name = get_object_name(obj_variable_name)
                h.write('RKEntityMapping *{} = [RKEntityMapping mappingForEntityForName:@"{}" inManagedObjectStore:managedObjectStore];\n'.format(name, obj_name))
               
                obj_fields = obj[obj_variable_name]
                attributes = []
                properties = []
                for key, value in obj_fields.iteritems():
                    if 'primarykey' in value:
                        primary_key = key
                        if primary_key == 'id':
                            primary_key = 'theID'
                        h.write('{}.identificationAttributes = @[@"{}"];\n'.format(name, primary_key))

                    values = value.split(',')
                    if "primarykey" in values:
                        values.remove("primarykey")
                    elif "optional" in values:
                        values.remove("optional")
                    
                    if "M2M" in values or "M2O" in values or "O2M" in values or "O2O" in values:
                        properties.append((key, values[1]))
                    elif "video" not in values and "image" not in values:  # don't create attributes for files
                        attributes.append(key)

                # Setup Attributes
                if len(attributes) > 0:
                    attribute_mappings = '[{} addAttributeMappingsFromDictionary:@{{'.format(name)
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

                property_mappings[name] = properties

        h.write("// Add all related mappings after we've created all the objects so we don't worry about ordering\n")
        for obj_name, properties in property_mappings.iteritems():
            if len(properties) > 0:
                for property_name, related_object_name in properties:
                    mapping_name = get_mapping_name(related_object_name)
                    h.write('[{0} addPropertyMapping:[RKRelationshipMapping relationshipMappingFromKeyPath:@"{1}" toKeyPath:@"{1}" withMapping:{2}]];\n'.format(obj_name, property_name, mapping_name))
        h.write('\n')

        print "URLs for Patches and Gets"
        print ''
        for url in urls:
            # Delete's don't need descriptors
            if 'patch' in url:
                create_request_descriptor(h, url, "patch")
                create_response_descriptor(h, url, "patch")

            if 'get' in url:
                create_response_descriptor(h, url, "get")

            if 'post' in url:
                create_request_descriptor(h, url, "post")
                create_response_descriptor(h, url, "post")
        h.write('\n')

        # DATA CALLS

        # GETS
        print "Gets with no ID's, ID's and no Parameters"
        print ''
        for url in urls:
            if 'get' in url:
                write_get_calls_to_files(url, h, m)
        h.write('\n')
        
        # GETS (PARAMETERS)
        print "Gets with parameters"
        print ''
        for url in urls:
            if 'get' in url and 'parameters' in url['get'] and url['get']['parameters'] != "":
                if url['url'] != "login/":
                    parameters = url['get']['parameters']
                    paras = params[parameters]
                    url_path = url['url']

                    write_doc_string(m, url, "get")

                    title = '- (void) get{}With'.format(sanitize_api_name(url_path))
                    for parameter in paras:
                        split = paras[parameter].split(',')
                        parameter_variable_name = get_parameter_variable_name(parameter)
                        title += "{}:({}){} ".format(parameter_variable_name.capitalize(),
                                                     OBJC_DATA_TYPES[split[0]],
                                                     parameter_variable_name)

                    success_failure_params = "success:(void (^)(RKObjectRequestOperation *operation, RKMappingResult *result))success failure:(void (^)(RKObjectRequestOperation *operation, NSError *error))failure"

                    h.write("{}{} {{\n".format(title, success_failure_params))
                    m.write("{}{};\n\n".format(title, success_failure_params))
                    h.write("    NSMutableDictionary* queryParams = [NSMutableDictionary dictionaryWithCapacity:{}];\n".format(len(paras)))

                    for parameter in paras:
                        parameter_variable_name = get_parameter_variable_name(parameter)
                        h.write("    if ({}) {{\n".format(parameter_variable_name))
                        h.write('      [queryParams setObject:{} forKey:@"{}"];\n'.format(parameter_variable_name, parameter))
                        h.write("    }\n")

                    write_shared_manager(h)
                    write_content_type(h, url['get'].get('content_type', 'json'))
                    h.write('    [sharedMgr getObjectsAtPath:@"{}" parameters:queryParams success:success failure:failure];\n'.format(url_path))
                    h.write('}\n\n')

            # POSTS
            if 'post' in url:
                post_request = requests[url['post']['request']]
                post_request_key = post_request.keys()[0]
                request_object = post_request[post_request_key]

                write_method_signature(h, m, request_object, url, "post")

                write_shared_manager(h)
                request_variable = post_request_key[1].capitalize() + post_request_key[2:]
                h.write('    {0} *obj = [NSEntityDescription insertNewObjectForEntityForName:@"{0}" inManagedObjectContext:sharedMgr.managedObjectStore.mainQueueManagedObjectContext];\n'.format(request_variable))

                assign_fields(h, request_object)
                path = check_and_write_for_id(h, url["url"])
                write_authentication(h, url['post']['#meta'])
                write_content_type(h, url['post'].get('content_type', 'json'))
                write_api_call(h, path, "post", request_object)

                h.write('}\n\n')

            # PATCH
            if 'patch' in url:
                if "id" in url['url']:
                    patch_request = requests[url['patch']['request']]
                    patch_request_key = patch_request.keys()[0]
                    request_object = patch_request[patch_request_key]

                    write_method_signature(h, m, request_object, url, "patch")

                    write_shared_manager(h)
                    request_variable = patch_request_key[1].capitalize() + patch_request_key[2:]
                    h.write('    {0} *obj = [NSEntityDescription insertNewObjectForEntityForName:@"{0}" inManagedObjectContext:sharedMgr.managedObjectStore.mainQueueManagedObjectContext];\n'.format(request_variable))

                    assign_fields(h, request_object)
                    write_authentication(h, url['patch']['#meta'])
                    write_content_type(h, url['patch'].get('content_type', 'json'))
                    path = check_and_write_for_id(h, url["url"])
                    write_api_call(h, path, "patch", request_object)

                    h.write('}\n\n')

            # DELETE
            if 'delete' in url:
                if "id" in url['url']:
                    write_method_signature(h, m, {}, url, "delete")
                    write_shared_manager(h)
                    write_authentication(h, url['delete']['#meta'])
                    write_content_type(h, url['delete'].get('content_type', 'json'))
                    path = check_and_write_for_id(h, url["url"])
                    write_api_call(h, path, "delete", {})
                    h.write('}\n\n')
        
        # LOGIN
        write_login_to_files(h, m)

        create_footer_for_h_file(m)
