  RKEntityMapping *postRequestMappingInverse = [postRequestMapping inverseMapping];
  postRequestMappingInverse.assignsDefaultValueForMissingAttributes = NO;
  RKRequestDescriptor *postWithIdPatchRequestDescriptor = [RKRequestDescriptor requestDescriptorWithMapping:[postRequestMapping inverseMapping] objectClass:[PostRequest class] rootKeyPath:nil method:RKRequestMethodPATCH];
  [objectManager addRequestDescriptor:postWithIdPatchRequestDescriptor];