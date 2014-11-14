# Add map to get Entities
# Create dynamic objects in the correct way
# need to add in content type
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
    "list"       : "NSArray*"
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

@interface DataModel : NSObject

+ (id)sharedDataModel;

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
    h_file.write('    RKObjectManager* sharedMgr = [RKObjectManager sharedManager];\n')

    write_authentication(h_file, url['get']['#meta'])
    api = check_and_write_for_id(h_file, url["url"])
    h_file.write('    [sharedMgr getObjectsAtPath:{} parameters:nil success:^(RKObjectRequestOperation *operation, RKMappingResult *mappingResult) {{\n'.format(api))
    h_file.write('       success(operation,mappingResult);\n')
    h_file.write('    } failure:^(RKObjectRequestOperation *operation, NSError *error) {\n')
    h_file.write('       RKLogError(@"Load failed with error: %@", error);\n')
    h_file.write('       failure(operation,error);\n')
    h_file.write('    }];\n')
    h_file.write('}\n\n')

    m_file.write("{};\n\n".format(method_signature))


def create_request_descriptor(h, url, method):
    info = url[method]
    object_variable_name = info['request']
    object_name = get_object_name(object_variable_name)
    descriptor_name = '{}RequestDescriptor'.format(create_descriptor_name(url['url']))
    mapping_name = get_mapping_name(object_variable_name)

    h.write('RKRequestDescriptor *{} = [RKRequestDescriptor requestDescriptorWithMapping:[{} inverseMapping] objectClass:[{} class] rootKeyPath:nil method:RKRequestMethod{}];\n'.format(descriptor_name, mapping_name, object_name, method.upper()))
    h.write('[objectManager addRequestDescriptor:{}];\n'.format(descriptor_name))
    h.write('\n')


def create_response_descriptor(h, url, method):
    info = url[method]
    object_variable_name = info['response']['200+']
    descriptor_name = '{}ResponseDescriptor'.format(create_descriptor_name(url['url']))
    mapping_name = get_mapping_name(object_variable_name)

    key_path = 'nil'
    if 'resource_type' in info:
        key_path = 'nil' if info['resource_type'] == 'detail' else '@"results"'
    elif method == "get":
        key_path = '@"results"'

    h.write('RKResponseDescriptor *{} = [RKResponseDescriptor responseDescriptorWithMapping:{} method:RKRequestMethod{} pathPattern:@"{}" keyPath:{} statusCodes:RKStatusCodeIndexSetForClass(RKStatusCodeClassSuccessful)];\n'.format(descriptor_name, mapping_name, method.upper(), url['url'], key_path))
    h.write('[objectManager addResponseDescriptor:{}];\n'.format(descriptor_name))
    h.write('\n')


def get_mapping_name(obj):
    return "{}{}Mapping".format(obj[1].lower(), obj[2:])


def get_object_name(obj):
    return obj[1].upper() + obj[2:]


def write_authentication(h, meta):
    # TODO: What to do about optional auth?
    if 'oauth2' in meta and 'optional' not in meta:
        h.write('    [sharedMgr.HTTPClient setDefaultHeader:@"Authorization" value:[NSString stringWithFormat:@"Bearer %@", [AppModel sharedModel].accessToken]];\n')


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

        # TODO: ideally we don't loop over objects twice, but easiest for now do to order of writing into .m file
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
                    else:
                        attributes.append(key)

                # Setup Attributes
                if len(attributes) > 0:
                    attribute_mappings = '[' + name + ' addAttributeMappingsFromDictionary:@{'
                    for attribute in attributes:
                        attribute_mappings += '@"' + attribute + '": '
                        if attribute == "id":
                            attribute = "theID"
                            attribute_mappings += '@"' + attribute + '",'
                        elif attribute == "description":
                            attribute = "theDescription"
                            attribute_mappings += '@"' + attribute + '",'
                        elif '_' in attribute:
                            words = attribute.split('_')
                            attribute = words[0]
                            for x in range(1,len(words)):
                                attribute += words[x].capitalize()
                            attribute_mappings += '@"' + attribute + '",'
                        else:
                            attribute_mappings += '@"' + attribute + '",'
                    attribute_mappings = attribute_mappings[:-1] + '}];\n'
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
            if 'patch' in url:
                create_request_descriptor(h, url, "patch")
                create_response_descriptor(h, url, "patch")
            elif 'get' in url and ':id' not in url['url']:
                create_response_descriptor(h, url, "get")
            elif 'post' in url:
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
                    name = url_path.split('/')[0]

                    write_doc_string(m, url, "get")

                    title = '- (void) get'+name.capitalize()+'With'
                    for par in paras:
                        split = paras[par].split(',')
                        if "__" in par:
                            parameter_names = par.split('__')
                            par = parameter_names[1]
                        elif "_" in par:
                            parameter_names = par.split('_')
                            par = parameter_names[1]     
                        title += par.capitalize() + ":(" + OBJC_DATA_TYPES[split[0]] + ")" + par + " "
                    h.write(title + "andSuccess:(void (^)(RKObjectRequestOperation *operation, RKMappingResult *result))success failure:(void (^)(RKObjectRequestOperation *operation, NSError *error))failure {\n")
                    m.write(title + "andSuccess:(void (^)(RKObjectRequestOperation *operation, RKMappingResult *result))success failure:(void (^)(RKObjectRequestOperation *operation, NSError *error))failure;\n\n")
                    h.write('    NSDictionary *queryParams;\n')
                    query_params = "queryParams = @{"
                    for par in paras:
                        our_par = par
                        if "__" in par:
                            parameter_names = par.split('__')
                            our_par = parameter_names[1]
                        elif "_" in par:
                            parameter_names = par.split('_')
                            our_par = parameter_names[1]  
                        query_params += '@"' + par + '": @"' + our_par + '", '
                    query_params = query_params[:-2] + "};\n"
                    h.write('    ' + query_params)
                    h.write('    [[RKObjectManager sharedManager] getObjectsAtPath:@"{}" parameters:queryParams success:^(RKObjectRequestOperation *operation, RKMappingResult *mappingResult) {{\n'.format(url_path))
                    h.write('       success(operation,mappingResult);\n')
                    h.write('    } failure:^(RKObjectRequestOperation *operation, NSError *error) {\n')
                    h.write('       RKLogError(@"Load failed with error: %@", error);\n')
                    h.write('       failure(operation,error);\n')
                    h.write('    }];\n')
                    h.write('}\n\n')

        for url in urls:
            # POSTS
            if 'post' in url:
                post_title = sanitize_api_name(url['url'])
                post_request = requests[url['post']['request']]
                post_request_key = post_request.keys()[0]
                method_title = '- (void) post'+post_title+'With'
                for field in post_request[post_request_key]:
                    title_variable = field.replace('_',"").capitalize()
                    variable_variable = field.replace('_',"")
                    variable_type = post_request[post_request_key][field].split(',')
                    variable_type = OBJC_DATA_TYPES[variable_type[0]]
                    method_title += title_variable+":("+variable_type+")"+variable_variable + " "
                if "id" in url['url']: 
                    method_title += "theID:(NSNumber*) theID "   
                method_title_h = method_title[:-1] + " success:(void (^)(RKObjectRequestOperation *operation, RKMappingResult *mappingResult))success failure:(void (^)(RKObjectRequestOperation *operation, NSError *error))failure;\n\n"
                method_title = method_title[:-1] + " success:(void (^)(RKObjectRequestOperation *operation, RKMappingResult *mappingResult))success failure:(void (^)(RKObjectRequestOperation *operation, NSError *error))failure {\n"
                h.write(method_title)

                write_doc_string(m, url, "post")
                m.write(method_title_h)

                h.write('    RKObjectManager* sharedMgr = [RKObjectManager sharedManager];\n')
                request_variable = post_request.keys()[0][1].capitalize() + post_request.keys()[0][2:]
                h.write('    {0} *obj = [NSEntityDescription insertNewObjectForEntityForName:@"{0}" inManagedObjectContext:sharedMgr.managedObjectStore.mainQueueManagedObjectContext];\n'.format(request_variable))
                for field in post_request[post_request_key]: 
                    obj_variable = field   
                    if obj_variable == "id":
                        obj_variable = "theID"
                    elif obj_variable == "description":
                        obj_variable = "theDescription"
                    elif '_' in obj_variable:
                        words = obj_variable.split('_')
                        obj_variable = words[0]
                        for x in range(1,len(words)):
                            next_word = words[x]
                            next_word = next_word.capitalize()
                            obj_variable += next_word

                    method_variable = field.replace('_', "")
                    h.write('    obj.'+obj_variable+' = ' + method_variable + ';\n') 
                url_destination = str(url['url'])
                write_authentication(h, url['post']['#meta'])
                h.write('    [sharedMgr postObject:obj path:@"{}" parameters:nil success:^(RKObjectRequestOperation *operation,\n'.format(url_destination))
                h.write('        RKMappingResult *mappingResult) {\n')
                h.write('        success(operation, mappingResult); }\n') 
                h.write('        failure:failure];\n')
                h.write('}\n\n')

            # PATCH
            elif 'patch' in url:
                if "id" in url['url']:
                    patch_title = sanitize_api_name(url['url'])
                    patch_request = requests[url['patch']['request']]
                    patch_request_key = patch_request.keys()[0]
                    method_title = '- (void) patch{}With'.format(patch_title)
                    for field in patch_request[patch_request_key]:
                        title_variable = field.replace('_', "").capitalize()
                        variable_variable = field.replace('_', "")
                        variable_type = patch_request[patch_request_key][field].split(',')
                        variable_type = OBJC_DATA_TYPES[variable_type[0]]
                        method_title += "{}:({}){} ".format(title_variable, variable_type, variable_variable)
                    method_title += "theID:(NSNumber*) theID "   
                    method_title_h = method_title[:-1] + " success:(void (^)(RKObjectRequestOperation *operation, RKMappingResult *mappingResult))success failure:(void (^)(RKObjectRequestOperation *operation, NSError *error))failure;\n\n"
                    method_title = method_title[:-1] + " success:(void (^)(RKObjectRequestOperation *operation, RKMappingResult *mappingResult))success failure:(void (^)(RKObjectRequestOperation *operation, NSError *error))failure {\n"
                    h.write(method_title)

                    write_doc_string(m, url, "patch")
                    m.write(method_title_h)

                    h.write('    RKObjectManager* sharedMgr = [RKObjectManager sharedManager];\n')
                    request_variable = patch_request_key[1].capitalize() + patch_request_key[2:]
                    h.write('    {0} *obj = [NSEntityDescription insertNewObjectForEntityForName:@"{0}" inManagedObjectContext:sharedMgr.managedObjectStore.mainQueueManagedObjectContext];\n'.format(request_variable))
                    for field in patch_request[patch_request_key]: 
                        obj_variable = field
                        if obj_variable == "id":
                            obj_variable = "theID"
                        elif obj_variable == "description":
                            obj_variable = "theDescription"
                        elif '_' in obj_variable:
                            words = obj_variable.split('_')
                            obj_variable = words[0]
                            for x in range(1, len(words)):
                                next_word = words[x]
                                obj_variable += next_word.capitalize()
                        method_variable = field.replace('_', "")
                        h.write('    obj.{} = {};\n'.format(obj_variable, method_variable))

                    write_authentication(h, url['patch']['#meta'])
                    api = check_and_write_for_id(h, url["url"])
                    h.write('    [sharedMgr patchObject:obj path:{} parameters:nil success:^(RKObjectRequestOperation *operation,\n'.format(api))
                    h.write('        RKMappingResult *mappingResult) {\n')
                    h.write('        success(operation, mappingResult); }\n') 
                    h.write('        failure:failure];\n')
                    h.write('}\n\n')
        
        # LOGIN
        write_login_to_files(h, m)

        create_footer_for_h_file(m)
