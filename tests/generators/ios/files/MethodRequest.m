  PostRequest *obj = [NSEntityDescription insertNewObjectForEntityForName:@"PostRequest" inManagedObjectContext:sharedMgr.managedObjectStore.mainQueueManagedObjectContext];
  obj.body = body;
  obj.title = title;
  [sharedMgr postObject:obj path:@"post/" parameters:nil success:success failure:failure];
