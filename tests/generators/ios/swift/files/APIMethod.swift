func getPostWithSuccess(success: RestKitSuccess, failure: RestKitError) {
  var sharedMgr = RKObjectManager.sharedManager()
  sharedMgr.requestSerializationMIMEType = RKMIMETypeJSON
  sharedMgr.HTTPClient.setDefaultHeader("Authorization", value: NSString.stringWithFormat("Bearer \(_delegate.getAccessToken())"))
  sharedMgr.getObject(nil, path: "post/", parameters: nil, success: success, failure: failure)
}