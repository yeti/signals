# Add map to get Entities
# Create dynamic objects in the correct way
# need to add in content type


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

my_dict = {}
dict_two = {}
params = {}

requests = {}


def write_login_to_files(h_file, m_file):
    h_file.write('\n')
    h_file.write('- (void)getAllLoginWithUsername:(NSString*)username password:(NSString*)password success:(void (^)(RKObjectRequestOperation *operation, RKMappingResult *mappingResult))success failure:(void (^)(RKObjectRequestOperation *operation, NSError *error))failure {\n')
    h_file.write('   RKObjectManager* sharedMgr = [RKObjectManager sharedManager];\n')
    h_file.write('   [sharedMgr.HTTPClient setAuthorizationHeaderWithUsername:username password:password];\n')
    h_file.write('   [sharedMgr getObjectsAtPath:@"login/" parameters:nil success:success failure:failure];\n')
    h_file.write('}\n')
    m_file.write('- (void)getAllLoginWithUsername:(NSString*)username password:(NSString*)password success:(void (^)(RKObjectRequestOperation *operation, RKMappingResult *mappingResult))success failure:(void (^)(RKObjectRequestOperation *operation, NSError *error))failure;\n')


def function():
        pass


def write_post_calls_to_files(name, is_id, url, h_file, m_file):
    if is_id:
        h_file.write('- (void)get'+name+'WithID:(NSNumber*)theID  andSuccess:(void (^)(RKObjectRequestOperation *operation, RKMappingResult *result))success failure:(void (^)(RKObjectRequestOperation *operation, NSError *error))failure{\n')
        m_file.write('- (void)get'+name+'WithID:(NSNumber*)theID  andSuccess:(void (^)(RKObjectRequestOperation *operation, RKMappingResult *result))success failure:(void (^)(RKObjectRequestOperation *operation, NSError *error))failure;\n')
    else:
        h_file.write('- (void)get'+name+'WithSuccess:(void (^)(RKObjectRequestOperation *operation, RKMappingResult *result))success failure:(void (^)(RKObjectRequestOperation *operation, NSError *error))failure{\n')
        m_file.write('- (void)get'+name+'WithSuccess:(void (^)(RKObjectRequestOperation *operation, RKMappingResult *result))success failure:(void (^)(RKObjectRequestOperation *operation, NSError *error))failure;\n')
    h_file.write('    [[RKObjectManager sharedManager] getObjectsAtPath:@"'+ url+'" parameters:nil success:^(RKObjectRequestOperation *operation, RKMappingResult *mappingResult) {\n')
    h_file.write('       success(operation,mappingResult);\n')
    h_file.write('    } failure:^(RKObjectRequestOperation *operation, NSError *error) {\n')
    h_file.write('       RKLogError(@"Load failed with error: %@", error);\n')
    h_file.write('       failure(operation,error);\n')
    h_file.write('    }];\n')
    h_file.write('}\n\n')


def create_mappings(urls, objects):

    #Mappings
    with open("MachineDataModel.m", "w") as h, open("MachineDataModel.h", 'w') as m:

        # Setup Mappings
        for obj in objects:

            if "Request" in obj.keys()[0]:
                requests[obj.keys()[0]] = obj

            params[obj.keys()[0]] = obj[obj.keys()[0]]

            if "Parameters" not in obj.keys()[0]:

                name = obj.keys()[0][1].lower() + obj.keys()[0][2:] +'Mapping'
                obj_name = obj.keys()[0][1].upper() + obj.keys()[0][2:];
                my_dict[obj_name] = name
                h.write('RKEntityMapping *' + name +' = [RKEntityMapping mappingForEntityForName:@"'+ obj_name +'" inManagedObjectStore:managedObjectStore];\n')
               
                obj_fields = obj[obj.keys()[0]]
                attributes = []
                properties = []
                for key, value in obj_fields.iteritems():
                    if 'primarykey' in value:
                        primarykey = key
                        if primarykey == 'id':
                            primarykey = 'theID'
                        h.write(name + '.identificationAttributes = @[@"' + primarykey + '"];\n')
                    values = value.split(',')
                    if "primarykey" in values:
                        values.remove("primarykey")
                    elif "optional" in values:
                        values.remove("optional")
                    
                    if "M2M" in values or "M2O" in values or "O2M" in values or "O2O" in values:
                        properties.append(key)
                        dict_two[key] = values[1][1:]
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

                # Setup Properties
                if len(properties) > 0:
                    for prop in properties:
                        #name = prop.capitalize() + 'Mapping'
                        mapping = dict_two[prop]
                        mapping = mapping[0].lower() + mapping[1:] + 'Mapping'
                        h.write('['+name+' addPropertyMapping:[RKRelationshipMapping relationshipMappingFromKeyPath:@"'+prop+'" toKeyPath:@"'+prop+'" withMapping:'+mapping+']];\n')
                h.write('\n')

        m.write('#import "MachineDataModel.h"\n')
        m.write('#import <RestKit/RestKit.h>\n')
        m.write('#import "Viddit-Swift.h"\n')

        for request in requests:
            request_variable = request[1].capitalize() + request[2:]
            m.write('#import "'+ request_variable +'.h";\n')

        print "URL's for Patches and Gets"
        print ''   
        for url in urls:
            url_api = url['url']
            get_info = None
            key_path = 'results'
            descriptor_name = None
            mapping = None
            if 'patch' in url:
                get_info = url['patch']
                key_path = 'nil'
                if 'keyPath' in url['patch']['response']:
                    key_path = get_info['response']['keyPath']
                descriptor_name = get_info['request'] + 'RequestPatchDescriptor'
                mapping = get_info['request'][1:]
                mapping = mapping[0].upper() + mapping[1:]
                h.write('RKRequestDescriptor *'+descriptor_name+' = [RKRequestDescriptor requestDescriptorWithMapping:['+my_dict[mapping]+' inverseMapping] objectClass:['+mapping+' class] rootKeyPath:nil method:RKRequestMethodPATCH];\n')
                h.write('[objectManager addRequestDescriptor:'+descriptor_name+'];\n')
                h.write('\n')
            elif 'get' in url and ':id' not in url['url']:
                meta = url['get']['#meta']
                get_info = url['get']
                descriptor_name = get_info['response']['200+'][1:] + 'Descriptor'
                mapping = get_info['response']['200+'][1:]
                mapping = mapping[0].upper() + mapping[1:]                
                h.write('RKResponseDescriptor *'+descriptor_name+' = [RKResponseDescriptor responseDescriptorWithMapping:'+my_dict[mapping]+' method:RKRequestMethodGET pathPattern:@"'+url_api+'" keyPath:@"'+key_path+'" statusCodes:RKStatusCodeIndexSetForClass(RKStatusCodeClassSuccessful)];\n')
                h.write('[objectManager addResponseDescriptor:'+descriptor_name+'];\n')
                h.write('\n')
            elif 'post' in url:
                meta = url['post']['#meta']
                get_info = url['post']
                if 'keyPath' in url['post']['response']:
                    key_path = get_info['response']['keyPath']
                    print key_path
                descriptor_name = get_info['request'][1:] + 'PostDescriptor'
                mapping = get_info['request'][1:]
                mapping = mapping[0].upper() + mapping[1:]  
                h.write('RKRequestDescriptor *'+descriptor_name+' = [RKRequestDescriptor requestDescriptorWithMapping:['+my_dict[mapping]+' inverseMapping] objectClass:['+mapping+' class] rootKeyPath:nil method:RKRequestMethodPOST];\n')
                h.write('[objectManager addRequestDescriptor:'+descriptor_name+'];\n')
                h.write('\n')
        h.write('\n')

        # DATA CALLS

        # GETS

        print "Gets with no ID's, ID's and no Parameters"
        print ''
        for url in urls:
            if 'get' in url:
                meta = url['get']['#meta']
                api = url['url']
                if ':id' not in url['url']:
                    if meta == '' or 'optional' in meta:
                        write_post_calls_to_files(api[:-1].capitalize(), False, api, h, m)
                else:
                    name = api.split('/')[0]
                    api = api.replace(":id", "theID")
                    write_post_calls_to_files(name.capitalize(), True, api, h, m)
        h.write('\n')
        
        # GETS (PARAMETERS)

        print "Gets with parameters"
        print ''
        login = None
        for url in urls:
            if 'get' in url and 'parameters' in url['get'] and url['get']['parameters'] != "":
                if url['url'] == "login/":
                    login = url
                else:
                    api = url['url']
                    parameters = url['get']['parameters']
                    paras = params[parameters]
                    url = url['url']
                    urls_split = url.split('/')
                    name = urls_split[0] 
                    title = '- (void)get'+name.capitalize()+'With'
                    for par in paras:
                        split = paras[par].split(',')
                        if "__" in par:
                            parameter_names = par.split('__')
                            par = parameter_names[1]
                        elif "_" in par:
                            parameter_names = par.split('_')
                            par = parameter_names[1]     
                        title += par.capitalize() + ":(" + OBJC_DATA_TYPES[split[0]] + ")" + par + " "
                    h.write(title + "andSuccess:(void (^)(RKObjectRequestOperation *operation, RKMappingResult *result))success failure:(void (^)(RKObjectRequestOperation *operation, NSError *error))failure{\n")
                    m.write(title + "andSuccess:(void (^)(RKObjectRequestOperation *operation, RKMappingResult *result))success failure:(void (^)(RKObjectRequestOperation *operation, NSError *error))failure;\n")
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
                    h.write('    [[RKObjectManager sharedManager] getObjectsAtPath:@"'+ url+'" parameters:queryParams success:^(RKObjectRequestOperation *operation, RKMappingResult *mappingResult) {\n')
                    h.write('       success(operation,mappingResult);\n')
                    h.write('    } failure:^(RKObjectRequestOperation *operation, NSError *error) {\n')
                    h.write('       RKLogError(@"Load failed with error: %@", error);\n')
                    h.write('       failure(operation,error);\n')
                    h.write('    }];\n')
                    h.write('}\n\n')

        for url in urls:
            
            # POSTS
            if 'post' in url:
                post_title = url['url'].replace('/',"").replace(":id",'')
                post_title = post_title.replace('_',"")
                post_title = post_title.capitalize()
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
                method_title_h = method_title[:-1] + " success:(void (^)(RKObjectRequestOperation *operation, RKMappingResult *mappingResult))success failure:(void (^)(RKObjectRequestOperation *operation, NSError *error))failure;\n"
                method_title = method_title[:-1] + " success:(void (^)(RKObjectRequestOperation *operation, RKMappingResult *mappingResult))success failure:(void (^)(RKObjectRequestOperation *operation, NSError *error))failure {\n"
                h.write(method_title)
                m.write(method_title_h)
                h.write('    RKObjectManager* sharedMgr = [RKObjectManager sharedManager];\n')
                request_variable = post_request.keys()[0][1].capitalize() + post_request.keys()[0][2:]
                h.write('    ' + request_variable + '* obj = [' + request_variable + ' new];\n')
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

                    method_variable = field.replace('_',"")
                    h.write('    obj.'+obj_variable+' = ' + method_variable + ';\n') 
                url_destination = str(url['url'])
                h.write('    [sharedMgr.HTTPClient setAuthorizationHeaderWithToken:[AppModel sharedModel].accessToken];\n')
                h.write('    [sharedMgr postObject:obj path:@"'+url_destination+'" parameters:nil success:^(RKObjectRequestOperation *operation,\n') 
                h.write('        RKMappingResult *mappingResult) {\n')
                h.write('        success(operation, mappingResult); }\n') 
                h.write('        failure:failure];\n')
                h.write('}\n')

            # PATCH
            elif 'patch' in url:
                if "id" in url['url']:
                    patch_title = url['url'].replace('/',"")
                    patch_title = patch_title.replace('_',"")
                    patch_title = patch_title.capitalize()
                    patch_title = patch_title[:-3]
                    patch_request = requests[url['patch']['request']]
                    patch_request_key = patch_request.keys()[0]
                    method_title = '- (void) patch'+patch_title+'With'
                    for field in patch_request[patch_request_key]:
                        title_variable = field.replace('_',"").capitalize()
                        variable_variable = field.replace('_',"")
                        variable_type = patch_request[patch_request_key][field].split(',')
                        variable_type = OBJC_DATA_TYPES[variable_type[0]]
                        method_title += title_variable+":("+variable_type+")"+variable_variable + " "
                    method_title += "theID:(NSNumber*) theID "   
                    method_title_h = method_title[:-1] + " success:(void (^)(RKObjectRequestOperation *operation, RKMappingResult *mappingResult))success failure:(void (^)(RKObjectRequestOperation *operation, NSError *error))failure;\n"
                    method_title = method_title[:-1] + " success:(void (^)(RKObjectRequestOperation *operation, RKMappingResult *mappingResult))success failure:(void (^)(RKObjectRequestOperation *operation, NSError *error))failure {\n"
                    h.write(method_title)
                    m.write(method_title_h)
                    h.write('    RKObjectManager* sharedMgr = [RKObjectManager sharedManager];\n')
                    request_variable = patch_request.keys()[0][1].capitalize() + patch_request.keys()[0][2:]
                    h.write('    ' + request_variable + '* obj = [' + request_variable + ' new];\n')
                    for field in patch_request[patch_request_key]: 
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
                        method_variable = field.replace('_',"")
                        h.write('    obj.'+obj_variable+' = ' + method_variable + ';\n') 
                    url_destination = str(url['url'])
                    h.write('    [sharedMgr.HTTPClient setAuthorizationHeaderWithToken:[AppModel sharedModel].accessToken];\n')
                    h.write('    [sharedMgr patchObject:obj path:@"'+url_destination+'" parameters:nil success:^(RKObjectRequestOperation *operation,\n') 
                    h.write('        RKMappingResult *mappingResult) {\n')
                    h.write('        success(operation, mappingResult); }\n') 
                    h.write('        failure:failure];\n')
                    h.write('}\n')                                                
        
        # LOGIN

        write_login_to_files(h, m)

if __name__ == "__main__":
    print 'Please enter your JSON file!'
    in_json = raw_input('--> ')
    create_mappings(in_json)
    # create_relationships_and_properties(in_json)