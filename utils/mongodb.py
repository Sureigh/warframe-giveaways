import json
from typing import Any, Dict, Union

import pymongo
from bson.objectid import ObjectId

with open('config.json', encoding='utf-8') as file:
    conn = json.load(file)['connection_string']

cluster = pymongo.MongoClient(conn)

class Cloud:
    cluster = cluster
    database = cluster['discord']
    collection = database['WFG']
    archive = database['archived_giveaways']

class Local(Cloud):
    cluster = pymongo.MongoClient("mongodb://localhost:27017/")

class TestCloud(Cloud):
    database = cluster['Test']

class Collection:
    def __init__(self, instance):
        self.collection = instance.collection
        self.archive = Archive(instance.archive)

    def delete(self, message_id: Union[int, ObjectId]):
        """Deletes a document by _id"""
        return self.collection.delete_one({'_id': str(message_id)})

    def truncate(self):
        """Clears the collection"""
        return self.collection.delete_many({})

    def find(self, _id: Union[int, str, ObjectId, None], return_cursor=False):
        """
        Queries database for value by key.
        :param _id: Searches document by _id, returns whole document if _id is None
        :param return_cursor:
        :return:
        """
        if _id is None:
            results = self.collection.find({})
            return [result for result in results] if return_cursor else results
        return self.collection.find_one({'_id': _id})

    def insert(self, _id: Union[int, str, ObjectId, dict], dict_: Dict[str, Any] = None):
        if type(_id) == dict:
            return self.collection.insert_one(_id)
        return self.collection.insert_one({
            '_id': _id,
            **dict_
        })

    def append(self, _id: int, dict_: Dict[str, Any]):
        return self.collection.update_one({'_id': _id}, {'$set': dict_})

    def update(self, _id: int, dict_: Dict[str, Any]):
        return self.collection.replace_one({'_id': _id}, dict_, upsert=True)

class Archive(Collection):
    def __init__(self, collection):  # noqa | using super.init will cause recursion
        self.collection = collection


if __name__ == '__main__':
    db = Collection(Cloud)
