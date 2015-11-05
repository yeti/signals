//
//  DataModel.m
//
//  Created by signals on %s.

#import "DataModel.h"
#import <CoreData/CoreData.h>
#import <RestKit/RestKit.h>

// Request object imports
#import "SignUpRequest.h"

@implementation DataModel

+ (DataModel *) sharedDataModel {
  static DataModel *__sharedDataModel = nil;
  static dispatch_once_t onceToken;
  dispatch_once(&onceToken, ^{
    __sharedDataModel = [[DataModel alloc] init];
  });

  return __sharedDataModel;
}

- (void) setup:(id<DataModelDelegate>)delegate {
  // Initialize RestKit
  _delegate = delegate;
  NSAssert(_delegate != NULL, @"delegate parameter cannot be NULL");
  NSURL *baseURL = [NSURL URLWithString:[_delegate getBaseURLString]];
  RKObjectManager *objectManager = [RKObjectManager managerWithBaseURL:baseURL];

  // Enable Activity Indicator Spinner
  [AFNetworkActivityIndicatorManager sharedManager].enabled = YES;

  // Initialize managed object store
  NSManagedObjectModel *managedObjectModel = [NSManagedObjectModel mergedModelFromBundles:nil];
  RKManagedObjectStore *managedObjectStore = [[RKManagedObjectStore alloc] initWithManagedObjectModel:managedObjectModel];

  objectManager.managedObjectStore = managedObjectStore;

  // MARK: RestKit Entity Mappings
  RKEntityMapping *loginResponseMapping = [RKEntityMapping mappingForEntityForName:@"LoginResponse" inManagedObjectStore:managedObjectStore];
  [loginResponseMapping addAttributeMappingsFromDictionary:@{@"client_secret": @"clientSecret", @"client_id": @"clientId"}];

  RKEntityMapping *signUpResponseMapping = [RKEntityMapping mappingForEntityForName:@"SignUpResponse" inManagedObjectStore:managedObjectStore];
  [signUpResponseMapping addAttributeMappingsFromDictionary:@{@"username": @"username", @"client_secret": @"clientSecret", @"fullname": @"fullname", @"email": @"email", @"client_id": @"clientId"}];

  RKEntityMapping *signUpRequestMapping = [RKEntityMapping mappingForEntityForName:@"SignUpRequest" inManagedObjectStore:managedObjectStore];
  [signUpRequestMapping addAttributeMappingsFromDictionary:@{@"username": @"username", @"fullname": @"fullname", @"password": @"password", @"email": @"email"}];


  // MARK: RestKit Entity Relationship Mappings
  // We place the relationship mappings after the entities so that we don't need to worry about ordering

  // MARK: RestKit URL Descriptors
  RKRequestDescriptor *signUpPostRequestDescriptor = [RKRequestDescriptor requestDescriptorWithMapping:[signUpRequestMapping inverseMapping] objectClass:[SignUpRequest class] rootKeyPath:nil method:RKRequestMethodPOST];
  [objectManager addRequestDescriptor:signUpPostRequestDescriptor];

  RKResponseDescriptor *signUpPostResponseDescriptor = [RKResponseDescriptor responseDescriptorWithMapping:signUpResponseMapping method:RKRequestMethodPOST pathPattern:@"sign_up/" keyPath:nil statusCodes:RKStatusCodeIndexSetForClass(RKStatusCodeClassSuccessful)];
  [objectManager addResponseDescriptor:signUpPostResponseDescriptor];

  RKResponseDescriptor *loginGetResponseDescriptor = [RKResponseDescriptor responseDescriptorWithMapping:loginResponseMapping method:RKRequestMethodGET pathPattern:@"login/" keyPath:@"results" statusCodes:RKStatusCodeIndexSetForClass(RKStatusCodeClassSuccessful)];
  [objectManager addResponseDescriptor:loginGetResponseDescriptor];


  /**
   Complete Core Data stack initialization
   */
  [managedObjectStore createPersistentStoreCoordinator];
  NSString *storePath = [RKApplicationDataDirectory() stringByAppendingPathComponent:@"TestProject.sqlite"];
  NSError *error;
  NSPersistentStore *persistentStore = [managedObjectStore addSQLitePersistentStoreAtPath:storePath fromSeedDatabaseAtPath:nil withConfiguration:nil options:nil error:&error];

  // Problem creating persistent store, wipe it since there was probably a core data change
  if (persistentStore == nil) {
    [[NSFileManager defaultManager] removeItemAtPath:storePath error:nil];
    persistentStore = [managedObjectStore addSQLitePersistentStoreAtPath:storePath fromSeedDatabaseAtPath:nil withConfiguration:nil options:nil error:&error];
  }

  NSAssert(persistentStore, @"Failed to add persistent store with error: %%@", error);

  // Create the managed object contexts
  [managedObjectStore createManagedObjectContexts];

  // Configure a managed object cache to ensure we do not create duplicate objects
  managedObjectStore.managedObjectCache = [[RKInMemoryManagedObjectCache alloc] initWithManagedObjectContext:managedObjectStore.persistentStoreManagedObjectContext];
}

// MARK: API Calls
- (void) postSignUpWithUsername:(NSString*)username fullname:(NSString*)fullname password:(NSString*)password email:(NSString*)email success:(void (^)(RKObjectRequestOperation *operation, RKMappingResult *mappingResult))success failure:(void (^)(RKObjectRequestOperation *operation, NSError *error))failure {
  RKObjectManager* sharedMgr = [RKObjectManager sharedManager];
  sharedMgr.requestSerializationMIMEType = RKMIMETypeJSON;
  SignUpRequest *obj = [NSEntityDescription insertNewObjectForEntityForName:@"SignUpRequest" inManagedObjectContext:sharedMgr.managedObjectStore.mainQueueManagedObjectContext];
  obj.username = username;
  obj.fullname = fullname;
  obj.password = password;
  obj.email = email;
  [sharedMgr postObject:obj path:@"sign_up/" parameters:nil success:success failure:failure];
}

- (void) getLoginWithSuccess:(void (^)(RKObjectRequestOperation *operation, RKMappingResult *mappingResult))success failure:(void (^)(RKObjectRequestOperation *operation, NSError *error))failure {
  RKObjectManager* sharedMgr = [RKObjectManager sharedManager];
  sharedMgr.requestSerializationMIMEType = RKMIMETypeJSON;
  [sharedMgr getObject:nil path:@"login/" parameters:nil success:success failure:failure];
}


@end