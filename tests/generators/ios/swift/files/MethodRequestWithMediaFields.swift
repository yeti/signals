    let obj = NSEntityDescription.insertNewObjectForEntityForName("PostRequest", inManagedObjectContext: sharedMgr.managedObjectStore.mainQueueManagedObjectContext) as! PostRequest
    obj.body = body
    obj.title = title
    if (video != nil || thumbnail != nil) {
      var request = sharedMgr.multipartFormRequestWithObject(obj, method: RKRequestMethod.POST, path: "post/", parameters: nil, constructingBodyWithBlock: { (formData: AFMultipartFormData) -> () in
        formData.appendPartWithFileURL(video, name: "video", fileName: "video.mp4", mimeType: "video/mp4", error: nil)
        formData.appendPartWithFileData(UIImageJPEGRepresentation(thumbnail, 1), name: "thumbnail", fileName: "thumbnail.jpeg", mimeType: "image/jpeg", error: nil)
      })

      var operation = sharedMgr.managedObjectRequestOperationWithRequest(request, managedObjectContext: nil, success: success, failure: failure)
      sharedMgr.enqueueObjectRequestOperation(operation)
    } else {
      sharedMgr.postObject(obj, path: "post/", parameters: nil, success: success, failure: failure)
    }
