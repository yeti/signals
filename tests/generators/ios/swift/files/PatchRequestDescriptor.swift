  var postRequestMappingInverse = postRequestMapping.inverseMapping()
  postRequestMappingInverse.assignsDefaultValueForMissingAttributes = false
  var postWithIdPatchRequestDescriptor = RKRequestDescriptor.requestDescriptorWithMapping(postRequestMapping.inverseMapping(), objectClass: PostRequest.self, rootKeyPath: nil, method: RKRequestMethodPATCH)
  objectManager.addRequestDescriptor(postWithIdPatchRequestDescriptor)