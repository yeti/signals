  PostRequest *obj = [NSEntityDescription insertNewObjectForEntityForName:@"PostRequest" inManagedObjectContext:sharedMgr.managedObjectStore.mainQueueManagedObjectContext];
  obj.body = body;
  obj.title = title;
  if (video != nil || thumbnail != nil) {
    NSMutableURLRequest *request = [sharedMgr multipartFormRequestWithObject:obj method:RKRequestMethodPOST path:@"post/" parameters:nil
                                                   constructingBodyWithBlock:^(id<AFMultipartFormData> formData) {
                                                     [formData appendPartWithFileURL:video name:@"video" fileName:@"video.mp4" mimeType:@"video/mp4" error:nil];
                                                     [formData appendPartWithFileData:UIImageJPEGRepresentation(thumbnail, 1)
                                                                                 name:@"thumbnail"
                                                                             fileName:@"thumbnail.jpeg"
                                                                             mimeType:@"image/jpeg"];
                                                   }];
    RKManagedObjectRequestOperation *operation = [sharedMgr managedObjectRequestOperationWithRequest:request managedObjectContext:nil success:success failure:failure];
    [sharedMgr enqueueObjectRequestOperation:operation];
  } else {
    [sharedMgr postObject:obj path:@"post/" parameters:nil success:success failure:failure];
  }
