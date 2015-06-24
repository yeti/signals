__author__ = 'rudy'


class Schema(object):
    # get_apis
    # post_apis
    # patch_apis
    # delete_apis
    # put_apis

    def __init__(self, schema_path):
        self.schema_path = schema_path


# abstract
class API(object):
    # url
    # doc
    # #meta
    # response
    pass


class GetAPI(API):
    pass


class PostAPI(API):
    pass


class PatchAPI(API):
    pass


class PutAPI(API):
    pass


class DeleteAPI(API):
    pass
