# MongoDB script to import JSON files from filespace for test fixtures.
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
        file_location = "{0}/*/*/*.json".format(THIS_DIR)
        print "Looking in {0}".format(file_location)
        for object_map_file in glob.iglob(file_location):
            db = object_map_file.split('/')[-3]
            collection = object_map_file.split('/')[-2]
            print "In {0} {1}".format(db, collection)
            with open(object_map_file, 'r') as source_file:
                mongo = MongoClient()['test_qbank_lite_' + db][collection]
                map = json.load(source_file)
                map['_id'] = ObjectId(map['_id'])
                if 'startDate' in map:
                    map['startDate'] = datetime.datetime(**map['startDate'])
                if 'endDate' in map:
                    map['endDate'] = datetime.datetime(**map['endDate'])

                try:
                    mongo.insert_one(map)
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
