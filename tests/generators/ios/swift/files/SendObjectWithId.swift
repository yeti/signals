    let formattedUrl = "post/\(theID)/"
    sharedMgr.patchObject(obj, path: formattedUrl, parameters: nil, success: success, failure: failure)
