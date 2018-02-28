import os
import sys

from dlkit.primordium.type.primitives import Type

from dlkit.runtime.utilities import impl_key_dict

if getattr(sys, 'frozen', False):
    ABS_PATH = os.path.dirname(sys.executable)
    TEST_ABS_PATH = ABS_PATH
else:
    PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
    ABS_PATH = '{0}'.format(os.path.abspath(os.path.join(PROJECT_PATH, os.pardir)))
    TEST_ABS_PATH = '{0}'.format(os.path.abspath(os.path.join(PROJECT_PATH, os.pardir)))

print('CWD is {}'.format(os.getcwd()))
print('ABSPATH is {}'.format(ABS_PATH))
os.chdir(ABS_PATH)

DATA_STORE_PATH = 'webapps/CLIx/datastore'
STUDENT_RESPONSE_DATA_STORE_PATH = 'webapps/CLIx/datastore/studentResponseFiles'

TEST_DATA_STORE_PATH = 'test_datastore'
TEST_STUDENT_RESPONSE_DATA_STORE_PATH = 'test_datastore/studentResponseFiles'

FILESYSTEM_ASSET_CONTENT_TYPE = Type(**
                                     {
                                         'authority': 'odl.mit.edu',
                                         'namespace': 'asset_content_record_type',
                                         'identifier': 'filesystem'
                                     })

###################################################
# PRODUCTION SETTINGS
###################################################

FILESYSTEM_ADAPTER_1 = {
    'id': 'filesystem_adapter_configuration_1',
    'displayName': 'Filesystem Adapter Configuration',
    'description': 'Configuration for Filesystem Adapter',
    'parameters': {
        'implKey': impl_key_dict('filesystem_adapter'),
        'repositoryProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Repository Provider Implementation',
            'description': 'Implementation for repository service provider',
            'values': [
                {'value': 'JSON_1', 'priority': 1}
            ]
        },
        'dataStorePath': {
            'syntax': 'STRING',
            'displayName': 'Path to local filesystem datastore',
            'description': 'Filesystem path for setting the MongoClient host.',
            'values': [
                {'value': DATA_STORE_PATH, 'priority': 1}  # Mac
            ]
        },
        'secondaryDataStorePath': {
            'syntax': 'STRING',
            'displayName': 'Path to local filesystem datastore',
            'description': 'Filesystem path for setting the MongoClient host.',
            'values': [
                {'value': STUDENT_RESPONSE_DATA_STORE_PATH, 'priority': 1}  # Mac
            ]
        },
        'dataStoreFullPath': {
            'syntax': 'STRING',
            'displayName': 'Full path to local filesystem datastore',
            'description': 'Filesystem path for setting the JSONClient host.',
            'values': [
                {'value': ABS_PATH, 'priority': 1}
            ]
        },
        'urlHostname': {
            'syntax': 'STRING',
            'displayName': 'Hostname config for serving files over the network',
            'description': 'Hostname config for serving files.',
            'values': [
                {'value': 'https://localhost:8080/api/v1', 'priority': 1}  # Mac
            ]
        },
    }
}

# FILESYSTEM_1 = {
#     'id': 'filesystem_configuration_1',
#     'displayName': 'Filesystem Configuration',
#     'description': 'Configuration for Filesystem Implementation',
#     'parameters': {
#         'implKey': impl_key_dict('filesystem'),
#         'recordsRegistry': {
#             'syntax': 'STRING',
#             'displayName': 'Python path to the extension records registry file',
#             'description': 'dot-separated path to the extension records registry file',
#             'values': [
#                 {'value': 'records.registry', 'priority': 1}
#             ]
#         },
#         'repositoryProviderImpl': {
#             'syntax': 'STRING',
#             'displayName': 'Repository Provider Implementation',
#             'description': 'Implementation for repository service provider',
#             'values': [
#                 {'value': 'FILESYSTEM_ADAPTER_1', 'priority': 1}
#             ]
#         },
#         'assetContentRecordTypeForFiles': {
#             'syntax': 'TYPE',
#             'displayName': 'Asset Content Type for Files',
#             'description': 'Asset Content Type for Records that store Files on local disk',
#             'values': [
#                 {'value': FILESYSTEM_ASSET_CONTENT_TYPE, 'priority': 1}
#             ]
#         },
#         'dataStorePath': {
#             'syntax': 'STRING',
#             'displayName': 'Path to local filesystem datastore',
#             'description': 'Filesystem path for setting the MongoClient host.',
#             'values': [
#                 {'value': DATA_STORE_PATH, 'priority': 1}
#             ]
#         },
#         'dataStoreFullPath': {
#             'syntax': 'STRING',
#             'displayName': 'Full path to local filesystem datastore',
#             'description': 'Filesystem path for setting the MongoClient host.',
#             'values': [
#                 {'value': ABS_PATH, 'priority': 1}
#             ]
#         },
#         'magicItemLookupSessions': {
#             'syntax': 'STRING',
#             'displayName': 'Which magic item lookup sessions to try',
#             'description': 'To handle magic IDs.',
#             'values': [
#                 {'value': 'records.assessment.clix.magic_item_lookup_sessions.CLIxMagicItemLookupSession', 'priority': 1}
#             ]
#         },
#         'useCachingForQualifierIds': {
#             'syntax': 'BOOLEAN',
#             'displayName': 'Flag to use memcached for authz qualifier_ids or not',
#             'description': 'Flag to use memcached for authz qualifier_ids or not',
#             'values': [
#                 {'value': True, 'priority': 1}
#             ]
#         },
#     },
# }
#
# MONGO_1 = {
#     'id': 'mongo_configuration_1',
#     'displayName': 'Mongo Configuration',
#     'description': 'Configuration for Mongo Implementation',
#     'parameters': {
#         'implKey': impl_key_dict('mongo'),
#         'repositoryProviderImpl': {
#             'syntax': 'STRING',
#             'displayName': 'Repository Provider Implementation',
#             'description': 'Implementation for repository service provider',
#             'values': [
#                 {'value': 'FILESYSTEM_ADAPTER_1', 'priority': 1}
#             ]
#         },
#         'assetContentRecordTypeForFiles': {
#             'syntax': 'TYPE',
#             'displayName': 'Asset Content Type for Files',
#             'description': 'Asset Content Type for Records that store Files on local disk',
#             'values': [
#                 {'value': FILESYSTEM_ASSET_CONTENT_TYPE, 'priority': 1}
#             ]
#         },
#         'recordsRegistry': {
#             'syntax': 'STRING',
#             'displayName': 'Python path to the extension records registry file',
#             'description': 'dot-separated path to the extension records registry file',
#             'values': [
#                 {'value': 'records.registry', 'priority': 1}
#             ]
#         },
#         'magicItemLookupSessions': {
#             'syntax': 'STRING',
#             'displayName': 'Which magic item lookup sessions to try',
#             'description': 'To handle magic IDs.',
#             'values': [
#                 {'value': 'records.assessment.clix.magic_item_lookup_sessions.CLIxMagicItemLookupSession', 'priority': 1}
#             ]
#         },
#         'localImpl': {
#             'syntax': 'STRING',
#             'displayName': 'Implementation identifier for local service provider',
#             'description': 'Implementation identifier for local service provider.  Typically the same identifier as the Mongo configuration',
#             'values': [
#                 {'value': 'MONGO_1', 'priority': 1}
#             ]
#         },
#         'useCachingForQualifierIds': {
#             'syntax': 'BOOLEAN',
#             'displayName': 'Flag to use memcached for authz qualifier_ids or not',
#             'description': 'Flag to use memcached for authz qualifier_ids or not',
#             'values': [
#                 {'value': True, 'priority': 1}
#             ]
#         },
#         'dataStoreFullPath': {
#             'syntax': 'STRING',
#             'displayName': 'Full path to local filesystem datastore',
#             'description': 'Filesystem path for setting the MongoClient host.',
#             'values': [
#                 {'value': ABS_PATH, 'priority': 1}
#             ]
#         },
#     }
# }

JSON_1 = {
    'id': 'json_configuration_1',
    'displayName': 'JSON Configuration',
    'description': 'Configuration for JSON Implementation',
    'parameters': {
        'implKey': impl_key_dict('json'),
        'repositoryProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Repository Provider Implementation',
            'description': 'Implementation for repository service provider',
            'values': [
                {'value': 'FILESYSTEM_ADAPTER_1', 'priority': 1}
            ]
        },
        'assetContentRecordTypeForFiles': {
            'syntax': 'TYPE',
            'displayName': 'Asset Content Type for Files',
            'description': 'Asset Content Type for Records that store Files on local disk',
            'values': [
                {'value': FILESYSTEM_ASSET_CONTENT_TYPE, 'priority': 1}
            ]
        },
        'recordsRegistry': {
            'syntax': 'STRING',
            'displayName': 'Python path to the extension records registry file',
            'description': 'dot-separated path to the extension records registry file',
            'values': [
                {'value': 'dlkit.records.registry', 'priority': 1}
            ]
        },
        'magicItemLookupSessions': {
            'syntax': 'STRING',
            'displayName': 'Which magic item lookup sessions to try',
            'description': 'To handle magic IDs.',
            'values': [
                {'value': 'dlkit.records.assessment.clix.magic_item_lookup_sessions.CLIxMagicItemLookupSession', 'priority': 1}
            ]
        },
        'localImpl': {
            'syntax': 'STRING',
            'displayName': 'Implementation identifier for local service provider',
            'description': 'Implementation identifier for local service provider.  Typically the same identifier as the Mongo configuration',
            'values': [
                {'value': 'JSON_1', 'priority': 1}
            ]
        },
        'useCachingForQualifierIds': {
            'syntax': 'BOOLEAN',
            'displayName': 'Flag to use caching for authz qualifier_ids or not',
            'description': 'Flag to use caching for authz qualifier_ids or not',
            'values': [
                {'value': True, 'priority': 1}
            ]
        },
        'cachingEngine': {
            'syntax': 'STRING',
            'displayName': 'Flag to configure caching engine',
            'description': 'Flag to configure caching engine',
            'values': [
                {'value': 'diskcache', 'priority': 1}  # can be either "memcache" or "diskcache"
            ]
        },
        'dataStorePath': {
            'syntax': 'STRING',
            'displayName': 'Path to local filesystem datastore',
            'description': 'Filesystem path for setting the JSONClient host.',
            'values': [
                {'value': DATA_STORE_PATH, 'priority': 1}
            ]
        },
        'dataStoreFullPath': {
            'syntax': 'STRING',
            'displayName': 'Full path to local filesystem datastore',
            'description': 'Filesystem path for setting the JSONClient host.',
            'values': [
                {'value': ABS_PATH, 'priority': 1}
            ]
        },
        'useFilesystem': {
            'syntax': 'BOOLEAN',
            'displayName': 'Use the filesystem instead of MongoDB',
            'description': 'Use the filesystem instead of MongoDB',
            'values': [
                {'value': True, 'priority': 1}
            ]
        },
    }
}

AUTHZ_ADAPTER_1 = {
    'id': 'authz_adapter_configuration_1',
    'displayName': 'AuthZ Adapter Configuration',
    'description': 'Configuration for AuthZ Adapter',
    'parameters': {
        'implKey': impl_key_dict('authz_adapter'),
        'authzAuthorityImpl': {
            'syntax': 'STRING',
            'displayName': 'Repository Provider Implementation',
            'description': 'Implementation for repository service provider',
            'values': [
                {'value': 'JSON_1', 'priority': 1}
            ]
        },
        'assessmentProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Assessment Provider Implementation',
            'description': 'Implementation for assessment service provider',
            'values': [
                {'value': 'JSON_1', 'priority': 1}
            ]
        },
        'authorizationProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Authorization Provider Implementation',
            'description': 'Implementation for authorization service provider',
            'values': [
                {'value': 'JSON_1', 'priority': 1}
            ]
        },
        'learningProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Learning Provider Implementation',
            'description': 'Implementation for learning service provider',
            'values': [
                {'value': 'JSON_1', 'priority': 1}
            ]
        },
        'hierarchyProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Hierarchy Provider Implementation',
            'description': 'Implementation for hierarchy service provider',
            'values': [
                {'value': 'JSON_1', 'priority': 1}
            ]
        },
        'repositoryProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Repository Provider Implementation',
            'description': 'Implementation for repository service provider',
            'values': [
                {'value': 'FILESYSTEM_ADAPTER_1', 'priority': 1}
            ]
        },
        'loggingProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Logging Provider Implementation',
            'description': 'Implementation for logging provider',
            'values': [
                {'value': 'JSON_1', 'priority': 1}
            ]
        },
    }
}

SERVICE = {
    'id': 'dlkit_runtime_bootstrap_configuration',
    'displayName': 'DLKit Runtime Bootstrap Configuration',
    'description': 'Bootstrap Configuration for DLKit Runtime',
    'parameters': {
        'implKey': impl_key_dict('service'),
        'assessmentProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Assessment Provider Implementation',
            'description': 'Implementation for assessment service provider',
            'values': [
                {'value': 'JSON_1', 'priority': 1}
            ]
        },
        'loggingProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Logging Provider Implementation',
            'description': 'Implementation for logging service provider',
            'values': [
                {'value': 'JSON_1', 'priority': 1}
            ]
        },
        'repositoryProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Repository Provider Implementation',
            'description': 'Implementation for repository service provider',
            'values': [
                {'value': 'FILESYSTEM_ADAPTER_1', 'priority': 1}
            ]
        },
        'learningProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Learning Provider Implementation',
            'description': 'Implementation for learning service provider',
            'values': [
                {'value': 'JSON_1', 'priority': 1}
            ]
        },
        'resourceProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Resource Provider Implementation',
            'description': 'Implementation for resource service provider',
            'values': [
                {'value': 'JSON_1', 'priority': 1}
            ]
        },
        'hierarchyProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Hierarchy Provider Implementation',
            'description': 'Implementation for hierarchy service provider',
            'values': [
                {'value': 'JSON_1', 'priority': 1}
            ]
        },
        'authorizationProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Authorization Provider Implementation',
            'description': 'Implementation for authorization service provider',
            'values': [
                {'value': 'JSON_1', 'priority': 1}
            ]
        },
    }
}

BOOTSTRAP = {
    'id': 'bootstrap_configuration',
    'displayName': 'BootStrap Configuration',
    'description': 'Configuration for Bootstrapping',
    'parameters': {
        'implKey': impl_key_dict('service'),
    }
}


###################################################
# TEST SETTINGS
###################################################

TEST_FILESYSTEM_ADAPTER_1 = {
    'id': 'filesystem_adapter_configuration_1',
    'displayName': 'Filesystem Adapter Configuration',
    'description': 'Configuration for Filesystem Adapter',
    'parameters': {
        'implKey': impl_key_dict('filesystem_adapter'),
        'repositoryProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Repository Provider Implementation',
            'description': 'Implementation for repository service provider',
            'values': [
                {'value': 'TEST_JSON_1', 'priority': 1}
            ]
        },
        'dataStorePath': {
            'syntax': 'STRING',
            'displayName': 'Path to local filesystem datastore',
            'description': 'Filesystem path for setting the MongoClient host.',
            'values': [
                {'value': TEST_DATA_STORE_PATH, 'priority': 1}  # Mac
            ]
        },
        'secondaryDataStorePath': {
            'syntax': 'STRING',
            'displayName': 'Path to local filesystem datastore',
            'description': 'Filesystem path for setting the MongoClient host.',
            'values': [
                {'value': TEST_STUDENT_RESPONSE_DATA_STORE_PATH, 'priority': 1}  # Mac
            ]
        },
        'dataStoreFullPath': {
            'syntax': 'STRING',
            'displayName': 'Full path to local filesystem datastore',
            'description': 'Filesystem path for setting the JSONClient host.',
            'values': [
                {'value': ABS_PATH, 'priority': 1}
            ]
        },
        'urlHostname': {
            'syntax': 'STRING',
            'displayName': 'Hostname config for serving files over the network',
            'description': 'Hostname config for serving files.',
            'values': [
                {'value': '/api/v1', 'priority': 1}  # Mac
            ]
        },
    }
}

# TEST_FILESYSTEM_1 = {
#     'id': 'filesystem_configuration_1',
#     'displayName': 'Filesystem Configuration',
#     'description': 'Configuration for Filesystem Implementation',
#     'parameters': {
#         'implKey': impl_key_dict('filesystem'),
#         'recordsRegistry': {
#             'syntax': 'STRING',
#             'displayName': 'Python path to the extension records registry file',
#             'description': 'dot-separated path to the extension records registry file',
#             'values': [
#                 {'value': 'records.registry', 'priority': 1}
#             ]
#         },
#         'repositoryProviderImpl': {
#             'syntax': 'STRING',
#             'displayName': 'Repository Provider Implementation',
#             'description': 'Implementation for repository service provider',
#             'values': [
#                 {'value': 'TEST_FILESYSTEM_ADAPTER_1', 'priority': 1}
#             ]
#         },
#         'assetContentRecordTypeForFiles': {
#             'syntax': 'TYPE',
#             'displayName': 'Asset Content Type for Files',
#             'description': 'Asset Content Type for Records that store Files on local disk',
#             'values': [
#                 {'value': FILESYSTEM_ASSET_CONTENT_TYPE, 'priority': 1}
#             ]
#         },
#         'dataStorePath': {
#             'syntax': 'STRING',
#             'displayName': 'Path to local filesystem datastore',
#             'description': 'Filesystem path for setting the MongoClient host.',
#             'values': [
#                 {'value': TEST_DATA_STORE_PATH, 'priority': 1}
#             ]
#         },
#         'dataStoreFullPath': {
#             'syntax': 'STRING',
#             'displayName': 'Full path to local filesystem datastore',
#             'description': 'Filesystem path for setting the MongoClient host.',
#             'values': [
#                 {'value': ABS_PATH, 'priority': 1}
#             ]
#         },
#         'magicItemLookupSessions': {
#             'syntax': 'STRING',
#             'displayName': 'Which magic item lookup sessions to try',
#             'description': 'To handle magic IDs.',
#             'values': [
#                 {'value': 'records.assessment.clix.magic_item_lookup_sessions.CLIxMagicItemLookupSession', 'priority': 1}
#             ]
#         },
#     },
#
# }
#
# TEST_MONGO_1 = {
#     'id': 'mongo_configuration_1',
#     'displayName': 'Mongo Configuration',
#     'description': 'Configuration for Mongo Implementation',
#     'parameters': {
#         'implKey': impl_key_dict('mongo'),
#         'mongoDBNamePrefix': {
#             'syntax': 'STRING',
#             'displayName': 'Mongo DB Name Prefix',
#             'description': 'Prefix for naming mongo databases.',
#             'values': [
#                 {'value': 'test_qbank_lite_', 'priority': 1}
#             ]
#         },
#         'repositoryProviderImpl': {
#             'syntax': 'STRING',
#             'displayName': 'Repository Provider Implementation',
#             'description': 'Implementation for repository service provider',
#             'values': [
#                 {'value': 'TEST_FILESYSTEM_ADAPTER_1', 'priority': 1}
#             ]
#         },
#         'assetContentRecordTypeForFiles': {
#             'syntax': 'TYPE',
#             'displayName': 'Asset Content Type for Files',
#             'description': 'Asset Content Type for Records that store Files on local disk',
#             'values': [
#                 {'value': FILESYSTEM_ASSET_CONTENT_TYPE, 'priority': 1}
#             ]
#         },
#         'recordsRegistry': {
#             'syntax': 'STRING',
#             'displayName': 'Python path to the extension records registry file',
#             'description': 'dot-separated path to the extension records registry file',
#             'values': [
#                 {'value': 'records.registry', 'priority': 1}
#             ]
#         },
#         'magicItemLookupSessions': {
#             'syntax': 'STRING',
#             'displayName': 'Which magic item lookup sessions to try',
#             'description': 'To handle magic IDs.',
#             'values': [
#                 {'value': 'records.assessment.clix.magic_item_lookup_sessions.CLIxMagicItemLookupSession', 'priority': 1}
#             ]
#         },
#         'localImpl': {
#             'syntax': 'STRING',
#             'displayName': 'Implementation identifier for local service provider',
#             'description': 'Implementation identifier for local service provider.  Typically the same identifier as the Mongo configuration',
#             'values': [
#                 {'value': 'TEST_MONGO_1', 'priority': 1}
#             ]
#         },
#         'useCachingForQualifierIds': {
#             'syntax': 'BOOLEAN',
#             'displayName': 'Flag to use memcached for authz qualifier_ids or not',
#             'description': 'Flag to use memcached for authz qualifier_ids or not',
#             'values': [
#                 {'value': True, 'priority': 1}
#             ]
#         },
#         'dataStoreFullPath': {
#             'syntax': 'STRING',
#             'displayName': 'Full path to local filesystem datastore',
#             'description': 'Filesystem path for setting the MongoClient host.',
#             'values': [
#                 {'value': TEST_ABS_PATH, 'priority': 1}
#             ]
#         },
#     }
# }

TEST_JSON_1 = {
    'id': 'json_configuration_1',
    'displayName': 'JSON Configuration',
    'description': 'Configuration for JSON MongoDB Implementation',
    'parameters': {
        'implKey': impl_key_dict('json'),
        'mongoDBNamePrefix': {
            'syntax': 'STRING',
            'displayName': 'Mongo DB Name Prefix',
            'description': 'Prefix for naming mongo databases.',
            'values': [
                {'value': 'test_qbank_lite_', 'priority': 1}
            ]
        },
        'repositoryProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Repository Provider Implementation',
            'description': 'Implementation for repository service provider',
            'values': [
                {'value': 'TEST_FILESYSTEM_ADAPTER_1', 'priority': 1}
            ]
        },
        'assetContentRecordTypeForFiles': {
            'syntax': 'TYPE',
            'displayName': 'Asset Content Type for Files',
            'description': 'Asset Content Type for Records that store Files on local disk',
            'values': [
                {'value': FILESYSTEM_ASSET_CONTENT_TYPE, 'priority': 1}
            ]
        },
        'recordsRegistry': {
            'syntax': 'STRING',
            'displayName': 'Python path to the extension records registry file',
            'description': 'dot-separated path to the extension records registry file',
            'values': [
                {'value': 'dlkit.records.registry', 'priority': 1}
            ]
        },
        'magicItemLookupSessions': {
            'syntax': 'STRING',
            'displayName': 'Which magic item lookup sessions to try',
            'description': 'To handle magic IDs.',
            'values': [
                {'value': 'dlkit.records.assessment.clix.magic_item_lookup_sessions.CLIxMagicItemLookupSession', 'priority': 1}
            ]
        },
        'localImpl': {
            'syntax': 'STRING',
            'displayName': 'Implementation identifier for local service provider',
            'description': 'Implementation identifier for local service provider.  Typically the same identifier as the Mongo configuration',
            'values': [
                {'value': 'TEST_JSON_1', 'priority': 1}
            ]
        },
        'useCachingForQualifierIds': {
            'syntax': 'BOOLEAN',
            'displayName': 'Flag to use memcached for authz qualifier_ids or not',
            'description': 'Flag to use memcached for authz qualifier_ids or not',
            'values': [
                {'value': True, 'priority': 1}
            ]
        },
        'cachingEngine': {
            'syntax': 'STRING',
            'displayName': 'Flag to configure caching engine',
            'description': 'Flag to configure caching engine',
            'values': [
                {'value': 'diskcache', 'priority': 1}
            ]
        },
        'dataStorePath': {
            'syntax': 'STRING',
            'displayName': 'Path to local filesystem datastore',
            'description': 'Filesystem path for setting the MongoClient host.',
            'values': [
                {'value': TEST_DATA_STORE_PATH, 'priority': 1}
            ]
        },
        'dataStoreFullPath': {
            'syntax': 'STRING',
            'displayName': 'Full path to local filesystem datastore',
            'description': 'Filesystem path for setting the MongoClient host.',
            'values': [
                {'value': TEST_ABS_PATH, 'priority': 1}
            ]
        },
        'useFilesystem': {
            'syntax': 'BOOLEAN',
            'displayName': 'Use the filesystem instead of MongoDB',
            'description': 'Use the filesystem instead of MongoDB',
            'values': [
                {'value': True, 'priority': 1}
            ]
        },
        'repositoryCatalogingProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Repository Cataloging Provider Implementation',
            'description': 'Cataloging Provider Implementation for Repository service',
            'values': [
                {'value': 'TEST_JSON_1', 'priority': 1}
            ]
        },
    }
}

TEST_AUTHZ_ADAPTER_1 = {
    'id': 'authz_adapter_configuration_1',
    'displayName': 'AuthZ Adapter Configuration',
    'description': 'Configuration for AuthZ Adapter',
    'parameters': {
        'implKey': impl_key_dict('authz_adapter'),
        'authzAuthorityImpl': {
            'syntax': 'STRING',
            'displayName': 'Repository Provider Implementation',
            'description': 'Implementation for repository service provider',
            'values': [
                {'value': 'TEST_JSON_1', 'priority': 1}
            ]
        },
        'assessmentProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Assessment Provider Implementation',
            'description': 'Implementation for assessment service provider',
            'values': [
                {'value': 'TEST_JSON_1', 'priority': 1}
            ]
        },
        'authorizationProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Authorization Provider Implementation',
            'description': 'Implementation for authorization service provider',
            'values': [
                {'value': 'TEST_JSON_1', 'priority': 1}
            ]
        },
        'learningProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Learning Provider Implementation',
            'description': 'Implementation for learning service provider',
            'values': [
                {'value': 'TEST_JSON_1', 'priority': 1}
            ]
        },
        'hierarchyProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Hierarchy Provider Implementation',
            'description': 'Implementation for hierarchy service provider',
            'values': [
                {'value': 'TEST_JSON_1', 'priority': 1}
            ]
        },
        'repositoryProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Repository Provider Implementation',
            'description': 'Implementation for repository service provider',
            'values': [
                {'value': 'TEST_FILESYSTEM_ADAPTER_1', 'priority': 1}
            ]
        },
        'loggingProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Logging Provider Implementation',
            'description': 'Implementation for logging provider',
            'values': [
                {'value': 'TEST_JSON_1', 'priority': 1}
            ]
        },
        'resourceProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Resource Provider Implementation',
            'description': 'Implementation for resource provider',
            'values': [
                {'value': 'TEST_JSON_1', 'priority': 1}
            ]
        },
    }
}

TEST_SERVICE = {
    'id': 'dlkit_runtime_bootstrap_configuration',
    'displayName': 'DLKit Runtime Bootstrap Configuration',
    'description': 'Bootstrap Configuration for DLKit Runtime',
    'parameters': {
        'implKey': impl_key_dict('service'),
        'assessmentProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Assessment Provider Implementation',
            'description': 'Implementation for assessment service provider',
            'values': [
                {'value': 'TEST_JSON_1', 'priority': 1}
            ]
        },
        'loggingProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Logging Provider Implementation',
            'description': 'Implementation for logging service provider',
            'values': [
                {'value': 'TEST_JSON_1', 'priority': 1}
            ]
        },
        'repositoryProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Repository Provider Implementation',
            'description': 'Implementation for repository service provider',
            'values': [
                {'value': 'TEST_FILESYSTEM_ADAPTER_1', 'priority': 1}
            ]
        },
        'learningProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Learning Provider Implementation',
            'description': 'Implementation for learning service provider',
            'values': [
                {'value': 'TEST_JSON_1', 'priority': 1}
            ]
        },
        'hierarchyProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Hierarchy Provider Implementation',
            'description': 'Implementation for hierarchy service provider',
            'values': [
                {'value': 'TEST_JSON_1', 'priority': 1}
            ]
        },
        'resourceProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Resource Provider Implementation',
            'description': 'Implementation for resource service provider',
            'values': [
                {'value': 'TEST_JSON_1', 'priority': 1}
            ]
        },
        'authorizationProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Authorization Provider Implementation',
            'description': 'Implementation for authorization service provider',
            'values': [
                {'value': 'TEST_JSON_1', 'priority': 1}
            ]
        },
    }
}
