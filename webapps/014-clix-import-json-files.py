# MongoDB script to import JSON files from filespace.
# * imports all JSON files from the given directory
#   (i.e. /var/www/webapps/CLIx/datastore)

import glob
import json
import os
import datetime

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from bson import ObjectId

THIS_DIR = os.path.dirname(os.path.realpath(__file__))


#-----------------------------------------------------------------------------

if __name__=='__main__':
    try:
        file_location = "{0}/CLIx/datastore/*/*/*.json".format(THIS_DIR)
        print "Looking in {0}".format(file_location)
        for object_map_file in glob.iglob(file_location):
            db = object_map_file.split('/')[-3]
            collection = object_map_file.split('/')[-2]
            print "In {0} {1}".format(db, collection)
            with open(object_map_file, 'r') as source_file:
                mongo = MongoClient()[db][collection]
                map = json.load(source_file)

                # Aliases don't need this
                if db != 'id':
                    map['_id'] = ObjectId(map['_id'])

                print "Found id {0}".format(str(map['_id']))
                if 'question' in map and map['question'] is not None:
                    map['question']['_id'] = ObjectId(map['question']['_id'])
                if 'answers' in map and map['answers'] is not []:
                    for answer in map['answers']:
                        answer['_id'] = ObjectId(answer['_id'])
                if 'assetContents' in map and map['assetContents'] is not []:
                    for asset_content in map['assetContents']:
                        asset_content['_id'] = ObjectId(asset_content['_id'])

                time_keys = ['creationTime', 'actualStartTime', 'completionTime',
                            'startDate', 'deadline']
                for time_key in time_keys:
                    if time_key in map and map[time_key] is not None:
                        map[time_key] = datetime.datetime(**map[time_key])
                if 'questions' in map and map['questions'] is not None:
                    for index, question in enumerate(map['questions']):
                        if 'responses' in question and question['responses'] is not None:
                            for response in question['responses']:
                                if response is not None and 'submissionTime' in response and response['submissionTime'] is not None:
                                    response['submissionTime'] == datetime.datetime(**response['submissionTime'])
                        map['questions'][index]['_id'] = ObjectId(question['_id'])
                try:
                    mongo.insert_one(map)
                except TypeError:
                    # for pymongo < 3
                    try:
                        mongo.insert(map)
                    except DuplicateKeyError:
                        mongo.save(map)
                except DuplicateKeyError:
                    mongo.save(map)
                print "Saving..."
    except:
        # http://stackoverflow.com/questions/1000900/how-to-keep-a-python-script-output-window-open#1000968
        import sys, traceback
        print sys.exc_info()[0]
        print traceback.format_exc()
    finally:
        print "Done! Press Enter to continue ..."
        raw_input()

