from vtstorage.mongo_command import MongoCommand
from pymongo import InsertOne, ReplaceOne, UpdateOne
from vtutils.misc import convert_mongo_result_to_dict
import os


class VTPermStorage():

    def __init__(self, type, connection, params=None):
        self._type = type
        self._connection = connection
        self._params = params
        if self._type == "mongo":
            self.mongo_command = MongoCommand(self._connection)
        self._bulk_actions = {}
        self.vt_env = os.getenv("VT_ENV", "development")

    def get_one(self, database=None, collection=None, query=None, projection=None):
        if self._type == "mongo":
            database = self.return_db(database)
            return self.mongo_command.get_one(database=database, collection=collection, query=query, projection=projection)

    def get_many(self, database=None, collection=None, query=None, limit=20, projection=None, start=0, sort=None, make_list=False):
        if self._type == "mongo":
            database = self.return_db(database)
            result_query = self.mongo_command.get_many(database=database, collection=collection, query=query,
                                              projection=projection, limit=limit, start=start, sort=sort)
            if make_list:
                return list(result_query)
            return result_query

    def get_all(self, database=None, collection=None, query=None, projection=None, sort=None):
        if self._type == "mongo":
            database = self.return_db(database)
            return self.mongo_command.get_all(database=database, collection=collection, query=query,
                                              projection=projection, sort=sort)

    def count(self, database=None, collection=None, query=None):
        if self._type == "mongo":
            database = self.return_db(database)
            if not query:
                return self.mongo_command.estimated_document_count(database=database, collection=collection, query=query)
            return self.mongo_command.count(database=database, collection=collection, query=query)

    def update_one(self, database=None, collection=None, query=None, set_object=None, options=None):
        if self._type == "mongo":
            database = self.return_db(database)
            set_object = self.clean_update_object(set_object)
            db_result = self.mongo_command.update_one(database=database, collection=collection, query=query,
                                                 set_object=set_object, options=options)
            return convert_mongo_result_to_dict(db_result)

    def find_one_and_update(self, database=None, collection=None, query=None, set_object=None, options=None):
        if self._type == "mongo":
            database = self.return_db(database)
            set_object = self.clean_update_object(set_object)
            db_result = self.mongo_command.find_one_and_update(database=database, collection=collection, query=query,
                                                 set_object=set_object, options=options)
            return convert_mongo_result_to_dict(db_result)

    def update_many(self, database=None, collection=None, query=None, set_object=None):
        if self._type == "mongo":
            database = self.return_db(database)
            set_object = self.clean_update_object(set_object)
            db_result = self.mongo_command.update_many(database=database, collection=collection, query=query,
                                                 set_object=set_object)
            return convert_mongo_result_to_dict(db_result)

    def insert_one(self, database=None, collection=None, set_object=None):
        if self._type == "mongo":
            database = self.return_db(database)
            db_result = self.mongo_command.insert(database=database, collection=collection, set_object=set_object)
            return convert_mongo_result_to_dict(db_result)

    def insert_many(self, database=None, collection=None, items=None):
        if self._type == "mongo":
            database = self.return_db(database)
            db_result = self.mongo_command.insert_many(database=database, collection=collection, items=items)
            return convert_mongo_result_to_dict(db_result)

    def replace_one(self, database=None, collection=None, query=None, set_object=None, upsert=False):
        if self._type == "mongo":
            database = self.return_db(database)
            db_result = self.mongo_command.replace_one(database=database, collection=collection, query=query,
                                                  set_object=set_object, upsert=upsert)
            return convert_mongo_result_to_dict(db_result)

    def delete_one(self, database=None, collection=None, query=None):
        if self._type == "mongo":
            database = self.return_db(database)
            db_result = self.mongo_command.delete_one(database=database, collection=collection, query=query)
            return convert_mongo_result_to_dict(db_result)

    def delete_many(self, database=None, collection=None, query=None):
        if self._type == "mongo":
            database = self.return_db(database)
            db_result = self.mongo_command.delete_many(database=database, collection=collection, query=query)
            return convert_mongo_result_to_dict(db_result)

    def return_db(self, database):
        if database:
            return database
        else:
            return self._params["database"]

    def aggregate(self, database=None, collection=None, pipeline=None):
        if self._type == "mongo":
            database = self.return_db(database)
            return self.mongo_command.aggregate(database=database, collection=collection, pipeline=pipeline)

    def clean_update_object(self, set_object):
        if set_object and "$set" in set_object and "_id" in set_object["$set"]:
            del set_object["$set"]["_id"]
        return set_object
