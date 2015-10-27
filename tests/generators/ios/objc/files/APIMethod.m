- (void) getPostWithSuccess:(void (^)(RKObjectRequestOperation *operation, RKMappingResult *mappingResult))success failure:(void (^)(RKObjectRequestOperation *operation, NSError *error))failure {
  RKObjectManager* sharedMgr = [RKObjectManager sharedManager];
  sharedMgr.requestSerializationMIMEType = RKMIMETypeJSON;
  [sharedMgr.HTTPClient setDefaultHeader:@"Authorization" value:[NSString stringWithFormat:@"Bearer %@", [_delegate getAccessToken]]];
  [sharedMgr getObject:nil path:@"post/" parameters:nil success:success failure:failure];
}