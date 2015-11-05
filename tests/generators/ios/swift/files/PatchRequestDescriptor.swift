    let postRequestMappingInverse = postRequestMapping.inverseMapping()
    postRequestMappingInverse.assignsDefaultValueForMissingAttributes = false
    let postWithIdPatchRequestDescriptor = RKRequestDescriptor(mapping: postRequestMapping.inverseMapping(), objectClass: PostRequest.self, rootKeyPath: nil, method: RKRequestMethod.PATCH)
    objectManager.addRequestDescriptor(postWithIdPatchRequestDescriptor)