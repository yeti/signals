    let queryParams = NSMutableDictionary(capacity: 2)
    if (userId) {
      queryParams.setObject(userId, forKey: "user_id")
    }
    if (title) {
      queryParams.setObject(title, forKey: "title")
    }
    sharedMgr.getObjectsAtPath("post/", parameters: queryParams, success: success, failure: failure)