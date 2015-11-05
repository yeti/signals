//
//  DataModel.h
//
//  Created by signals on %s.

#import <Foundation/Foundation.h>

@class RKObjectRequestOperation;
@class RKMappingResult;
@class UIImage;

@protocol DataModelDelegate <NSObject>

- (NSString*)getBaseURLString;
- (NSString*)getAccessToken;

@end


@interface DataModel : NSObject

+ (DataModel *)sharedDataModel;
@property (weak) id <DataModelDelegate> delegate;

/**

  MARK: sign_up/
  Creates a new user and returns client_id and client_secret

*/

- (void) postSignUpWithUsername:(NSString*)username fullname:(NSString*)fullname password:(NSString*)password email:(NSString*)email success:(void (^)(RKObjectRequestOperation *operation, RKMappingResult *mappingResult))success failure:(void (^)(RKObjectRequestOperation *operation, NSError *error))failure;

/**

  MARK: login/
  Authenticates an existing user and returns client_id and client_secret

*/

- (void) getLoginWithSuccess:(void (^)(RKObjectRequestOperation *operation, RKMappingResult *mappingResult))success failure:(void (^)(RKObjectRequestOperation *operation, NSError *error))failure;


- (void) setup:(id<DataModelDelegate>)delegate;

@end