//
//  DataModel.swift
//
//  Created by signals on %s.

import Foundation
import CoreData
import RestKit

typealias RestKitSuccess = (operation: RKObjectRequestOperation!, result: RKMappingResult!) -> Void
typealias RestKitError = (operation: RKObjectRequestOperation!, error: NSError!) -> Void

protocol DataModelDelegate {
  func getBaseURLString() -> String
  func getAccessToken() -> String
}

class DataModel: NSObject {
  var delegate: DataModelDelegate?

  class func sharedDataModel() -> DataModel {
    struct Static {
      static var __sharedDataModel: DataModel? = nil
      static var onceToken: dispatch_once_t = 0
    }

    dispatch_once(&Static.onceToken) {
      Static.__sharedDataModel = DataModel.init()
    }

    return Static.__sharedDataModel!
  }

  func setup(delegate: DataModelDelegate) {
    // Initialize RestKit
    let _delegate = delegate
    self.delegate = delegate
    let baseURL = NSURL(string: _delegate.getBaseURLString())
    let objectManager = RKObjectManager(baseURL: baseURL)

    // Enable Activity Indicator Spinner
    AFNetworkActivityIndicatorManager.sharedManager().enabled = true

    // Initialize managed object store
    let managedObjectModel = NSManagedObjectModel.mergedModelFromBundles(nil)
    let managedObjectStore = RKManagedObjectStore(managedObjectModel: managedObjectModel)

    objectManager.managedObjectStore = managedObjectStore

    // MARK: RestKit Entity Mappings
    let loginResponseMapping = RKEntityMapping(forEntityForName: "LoginResponse", inManagedObjectStore: managedObjectStore)
    loginResponseMapping.addAttributeMappingsFromDictionary([ "client_secret": "clientSecret", "client_id": "clientId" ])

    let signUpResponseMapping = RKEntityMapping(forEntityForName: "SignUpResponse", inManagedObjectStore: managedObjectStore)
    signUpResponseMapping.addAttributeMappingsFromDictionary([ "username": "username", "client_secret": "clientSecret", "fullname": "fullname", "email": "email", "client_id": "clientId" ])

    let signUpRequestMapping = RKEntityMapping(forEntityForName: "SignUpRequest", inManagedObjectStore: managedObjectStore)
    signUpRequestMapping.addAttributeMappingsFromDictionary([ "username": "username", "fullname": "fullname", "password": "password", "email": "email" ])


    // MARK: RestKit Entity Relationship Mappings
    // We place the relationship mappings after the entities so that we don't need to worry about ordering

    // MARK: RestKit URL Descriptors
    let signUpPostRequestDescriptor = RKRequestDescriptor(mapping: signUpRequestMapping.inverseMapping(), objectClass: SignUpRequest.self, rootKeyPath: nil, method: RKRequestMethod.POST)
    objectManager.addRequestDescriptor(signUpPostRequestDescriptor)

    let signUpPostResponseDescriptor = RKResponseDescriptor(mapping: signUpResponseMapping, method: RKRequestMethod.POST, pathPattern: "sign_up/", keyPath: nil, statusCodes: RKStatusCodeIndexSetForClass(RKStatusCodeClass.Successful))
    objectManager.addResponseDescriptor(signUpPostResponseDescriptor)

    let loginGetResponseDescriptor = RKResponseDescriptor(mapping: loginResponseMapping, method: RKRequestMethod.GET, pathPattern: "login/", keyPath: "results", statusCodes: RKStatusCodeIndexSetForClass(RKStatusCodeClass.Successful))
    objectManager.addResponseDescriptor(loginGetResponseDescriptor)


    /**
    Complete Core Data stack initialization
    */
    managedObjectStore.createPersistentStoreCoordinator()
    let storePath = (RKApplicationDataDirectory() as NSString).stringByAppendingPathComponent("TestProject.sqlite")

    do {
      try managedObjectStore.addSQLitePersistentStoreAtPath(storePath, fromSeedDatabaseAtPath: nil, withConfiguration: nil, options: nil)
    } catch {
      // Problem creating persistent store, wipe it since there was probably a core data change
      // Causes runtime crash if still unable to create persistant storage
      try! NSFileManager.defaultManager().removeItemAtPath(storePath)
      try! managedObjectStore.addSQLitePersistentStoreAtPath(storePath, fromSeedDatabaseAtPath: nil, withConfiguration: nil, options: nil)
    }

    // Create the managed object contexts
    managedObjectStore.createManagedObjectContexts()

    // Configure a managed object cache to ensure we do not create duplicate objects
    managedObjectStore.managedObjectCache = RKInMemoryManagedObjectCache(managedObjectContext: managedObjectStore.persistentStoreManagedObjectContext)
  }

  // MARK: API Calls
  func postSignUpWithUsername(username: String, fullname: String, password: String, email: String, success: RestKitSuccess, failure: RestKitError) {
    let sharedMgr = RKObjectManager.sharedManager()
    sharedMgr.requestSerializationMIMEType = RKMIMETypeJSON
    let obj = NSEntityDescription.insertNewObjectForEntityForName("SignUpRequest", inManagedObjectContext: sharedMgr.managedObjectStore.mainQueueManagedObjectContext) as! SignUpRequest
    obj.username = username
    obj.fullname = fullname
    obj.password = password
    obj.email = email
    sharedMgr.postObject(obj, path: "sign_up/", parameters: nil, success: success, failure: failure)
  }

  func getLoginWithSuccess(success: RestKitSuccess, failure: RestKitError) {
    let sharedMgr = RKObjectManager.sharedManager()
    sharedMgr.requestSerializationMIMEType = RKMIMETypeJSON
    sharedMgr.getObject(nil, path: "login/", parameters: nil, success: success, failure: failure)
  }

}