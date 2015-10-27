  RKEntityMapping *postResponseMapping = [RKEntityMapping mappingForEntityForName:@"PostResponse" inManagedObjectStore:managedObjectStore];
  postResponseMapping.identificationAttributes = @[@"theID"];
  [postResponseMapping addAttributeMappingsFromDictionary:@{@"body": @"body", @"id": @"theID", @"title": @"title"}];
