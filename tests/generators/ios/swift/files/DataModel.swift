//
//  DataModel.swift
//
//  Created by signals on %s.

import Foundation
import CoreData
import RestKit

typealias RestKitSuccess = (operation: RKObjectRequestOperation!, result: RKMappingResult!) -> Void
typealias RestKitError = (operation: RKObjectRequestOperation!, error: NSError!) -> Void

@objc public class DataModel: NSObject {
  var getBaseURLString: String?
  var getAccessToken: String?

  class var sharedDataModel: DataModel {
    struct Static {
      static var __sharedDataModel = nil
      static var onceToken: dispatch_once_t = 0
    }

    dispatch_once(&Static.onceToken) {
      __sharedDataModel = DataModel.alloc().init()
    }

    return Static.__sharedDataModel!
  }
}

func setup(delegate: DataModelDelegate) {
  // Initialize RestKit
  _delegate = delegate;
  assert(_delegate != nil, "delegate parameter cannot be nil")
  var baseURL = NSURL.URLWithString(_delegate.getBaseURLString())
  var objectManager = RKObjectManager.managerWithBaseURL(baseURL)

  // Enable Activity Indicator Spinner
  AFNetworkActivityIndicatorManager.sharedManager().enabled = true;

  // Initialize managed object store
  var managedObjectModel = NSManagedObjectModel.mergedModelFromBundles(nil)
  var managedObjectStore = RKManagedObjectStore.alloc().initWithManagedObjectModel(managedObjectModel)

  objectManager.managedObjectStore = managedObjectStore;

  // MARK: RestKit Entity Mappings
  var loginResponseMapping = RKEntityMapping.mappingForEntityForName(LoginResponse, inManagedObjectStore: managedObjectStore)
  loginResponseMapping.addAttributeMappingsFromDictionary([ "client_secret": "clientSecret", "client_id": "clientId" ])

  var signUpResponseMapping = RKEntityMapping.mappingForEntityForName(SignUpResponse, inManagedObjectStore: managedObjectStore)
  signUpResponseMapping.addAttributeMappingsFromDictionary([ "username": "username", "client_secret": "clientSecret", "fullname": "fullname", "email": "email", "client_id": "clientId" ])

  var signUpRequestMapping = RKEntityMapping.mappingForEntityForName(SignUpRequest, inManagedObjectStore: managedObjectStore)
  signUpRequestMapping.addAttributeMappingsFromDictionary([ "username": "username", "fullname": "fullname", "password": "password", "email": "email" ])


  // MARK: RestKit Entity Relationship Mappings
  // We place the relationship mappings after the entities so that we don't need to worry about ordering

  // MARK: RestKit URL Descriptors
  var signUpPostRequestDescriptor = RKRequestDescriptor.requestDescriptorWithMapping(signUpRequestMapping.inverseMapping(), objectClass: SignUpRequest.self, rootKeyPath: nil, method: RKRequestMethodPOST)
  objectManager.addRequestDescriptor(signUpPostRequestDescriptor)

  var signUpPostResponseDescriptor = RKResponseDescriptor.responseDescriptorWithMapping(signUpResponseMapping, method: RKRequestMethodPOST, pathPattern: "sign_up/", keyPath: nil, statusCodes: RKStatusCodeIndexSetForClass(RKStatusCodeClassSuccessful))
  objectManager.addResponseDescriptor(signUpPostResponseDescriptor)

  var loginGetResponseDescriptor = RKResponseDescriptor.responseDescriptorWithMapping(loginResponseMapping, method: RKRequestMethodGET, pathPattern: "login/", keyPath: "results", statusCodes: RKStatusCodeIndexSetForClass(RKStatusCodeClassSuccessful))
  objectManager.addResponseDescriptor(loginGetResponseDescriptor)


  /**
   Complete Core Data stack initialization
   */
  managedObjectStore.createPersistentStoreCoordinator()
  var storePath = RKApplicationDataDirectory().stringByAppendingPathComponent("TestProject.sqlite")
  var error: NSError
  var persistentStore = managedObjectStore.addSQLitePersistentStoreAtPath(storePath, fromSeedDatabaseAtPath: nil, withConfiguration: nil, options: nil, error: &error)

  // Problem creating persistent store, wipe it since there was probably a core data change
  if (persistentStore == nil) {
    NSFileManager.defaultManager().removeItemAtPath(storePath, error: nil)
    persistentStore = managedObjectStore.addSQLitePersistentStoreAtPath(storePath, fromSeedDatabaseAtPath: nil, withConfiguration: nil, options: nil, error: &error)
  }

  assert(persistentStore, "Failed to add persistent store with error: \(error)")

  // Create the managed object contexts
  managedObjectStore.createManagedObjectContexts()

  // Configure a managed object cache to ensure we do not create duplicate objects
  managedObjectStore.managedObjectCache = RKInMemoryManagedObjectCache.alloc().initWithManagedObjectContext(managedObjectStore.persistentStoreManagedObjectContext)
}

// MARK: API Calls
func postSignUpWithUsername(username: String, fullname: String, password: String, email: String, success: RestKitSuccess, failure: RestKitError) {
  var sharedMgr = RKObjectManager.sharedManager()
  sharedMgr.requestSerializationMIMEType = RKMIMETypeJSON
  var obj = NSEntityDescription.insertNewObjectForEntityForName(SignUpRequest, inManagedObjectContext: sharedMgr.managedObjectStore.mainQueueManagedObjectContext)
  obj.username = username
  obj.fullname = fullname
  obj.password = password
  obj.email = email
  sharedMgr.postObject(obj, path: "sign_up/", parameters: nil, success: success, failure: failure)
}

func getLoginWithSuccess(success: RestKitSuccess, failure: RestKitError) {
  var sharedMgr = RKObjectManager.sharedManager()
  sharedMgr.requestSerializationMIMEType = RKMIMETypeJSON
  sharedMgr.getObject(nil, path: "login/", parameters: nil, success: success, failure: failure)
}

func getAllLoginWithUsername(username: String, password: String, success: RestKitSuccess, failure: RestKitFailure) {
  var sharedMgr = RKObjectManager.sharedManager()
  sharedMgr.HTTPClient.setAuthorizationHeaderWithUsername(username, password: password)
  sharedMgr.requestSerializationMIMEType = RKMIMETypeFormURLEncoded
  sharedMgr.getObjectsAtPath("login/", parameters: nil, success: success, failure: failure)
}