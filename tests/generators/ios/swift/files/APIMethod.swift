  func getPostWithSuccess(success: RestKitSuccess, failure: RestKitError) {
    let sharedMgr = RKObjectManager.sharedManager()
    sharedMgr.requestSerializationMIMEType = RKMIMETypeJSON
    sharedMgr.HTTPClient.setDefaultHeader("Authorization", value: NSString(format: "Bearer \(delegate!.getAccessToken())") as String)
    sharedMgr.getObject(nil, path: "post/", parameters: nil, success: success, failure: failure)
  }