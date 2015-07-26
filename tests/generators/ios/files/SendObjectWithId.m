  NSString* formattedUrl = [NSString stringWithFormat:@"post/%@/", theID];
  [sharedMgr patchObject:obj path:formattedUrl parameters:nil success:success failure:failure];
