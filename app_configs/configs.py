import os
import sys

from dlkit.primordium.type.primitives import Type

from dlkit_runtime.utilities import impl_key_dict

if getattr(sys, 'frozen', False):
    ABS_PATH = os.path.dirname(sys.executable)
else:
    PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
    ABS_PATH = '{0}'.format(os.path.abspath(os.path.join(PROJECT_PATH, os.pardir)))


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
                {'value': 'FILESYSTEM_1', 'priority': 1}
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
        'urlHostname': {
            'syntax': 'STRING',
            'displayName': 'Hostname config for serving files over the network',
            'description': 'Hostname config for serving files.',
            'values': [
                {'value': 'https://qbank-clix-dev.mit.edu/api/v1', 'priority': 1}  # Mac
            ]
        },
    }
}

FILESYSTEM_1 = {
    'id': 'filesystem_configuration_1',
    'displayName': 'Filesystem Configuration',
    'description': 'Configuration for Filesystem Implementation',
    'parameters': {
        'implKey': impl_key_dict('filesystem'),
        'recordsRegistry': {
            'syntax': 'STRING',
            'displayName': 'Python path to the extension records registry file',
            'description': 'dot-separated path to the extension records registry file',
            'values': [
                {'value': 'records.registry', 'priority': 1}
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
        'assetContentRecordTypeForFiles': {
            'syntax': 'TYPE',
            'displayName': 'Asset Content Type for Files',
            'description': 'Asset Content Type for Records that store Files on local disk',
            'values': [
                {'value': FILESYSTEM_ASSET_CONTENT_TYPE, 'priority': 1}
            ]
        },
        'dataStorePath': {
            'syntax': 'STRING',
            'displayName': 'Path to local filesystem datastore',
            'description': 'Filesystem path for setting the MongoClient host.',
            'values': [
                {'value': DATA_STORE_PATH, 'priority': 1}
            ]
        },
        'dataStoreFullPath': {
            'syntax': 'STRING',
            'displayName': 'Full path to local filesystem datastore',
            'description': 'Filesystem path for setting the MongoClient host.',
            'values': [
                {'value': ABS_PATH, 'priority': 1}
            ]
        },
        'magicItemLookupSessions': {
            'syntax': 'STRING',
            'displayName': 'Which magic item lookup sessions to try',
            'description': 'To handle magic IDs.',
            'values': [
                {'value': 'records.assessment.clix.magic_item_lookup_sessions.CLIxMagicItemLookupSession', 'priority': 1}
            ]
        },
    },

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
                {'value': 'FILESYSTEM_1', 'priority': 1}
            ]
        },
        'assessmentProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Assessment Provider Implementation',
            'description': 'Implementation for assessment service provider',
            'values': [
                {'value': 'FILESYSTEM_1', 'priority': 1}
            ]
        },
        'authorizationProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Authorization Provider Implementation',
            'description': 'Implementation for authorization service provider',
            'values': [
                {'value': 'FILESYSTEM_1', 'priority': 1}
            ]
        },
        'learningProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Learning Provider Implementation',
            'description': 'Implementation for learning service provider',
            'values': [
                {'value': 'FILESYSTEM_1', 'priority': 1}
            ]
        },
        'hierarchyProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Hierarchy Provider Implementation',
            'description': 'Implementation for hierarchy service provider',
            'values': [
                {'value': 'FILESYSTEM_1', 'priority': 1}
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
                {'value': 'FILESYSTEM_1', 'priority': 1}
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
                {'value': 'FILESYSTEM_1', 'priority': 1}
            ]
        },
        'loggingProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Logging Provider Implementation',
            'description': 'Implementation for logging service provider',
            'values': [
                {'value': 'FILESYSTEM_1', 'priority': 1}
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
                {'value': 'FILESYSTEM_1', 'priority': 1}
            ]
        },
        'hierarchyProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Hierarchy Provider Implementation',
            'description': 'Implementation for hierarchy service provider',
            'values': [
                {'value': 'FILESYSTEM_1', 'priority': 1}
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
                {'value': 'TEST_FILESYSTEM_1', 'priority': 1}
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

TEST_FILESYSTEM_1 = {
    'id': 'filesystem_configuration_1',
    'displayName': 'Filesystem Configuration',
    'description': 'Configuration for Filesystem Implementation',
    'parameters': {
        'implKey': impl_key_dict('filesystem'),
        'recordsRegistry': {
            'syntax': 'STRING',
            'displayName': 'Python path to the extension records registry file',
            'description': 'dot-separated path to the extension records registry file',
            'values': [
                {'value': 'records.registry', 'priority': 1}
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
                {'value': ABS_PATH, 'priority': 1}
            ]
        },
        'magicItemLookupSessions': {
            'syntax': 'STRING',
            'displayName': 'Which magic item lookup sessions to try',
            'description': 'To handle magic IDs.',
            'values': [
                {'value': 'records.assessment.clix.magic_item_lookup_sessions.CLIxMagicItemLookupSession', 'priority': 1}
            ]
        },
    },

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
                {'value': 'TEST_FILESYSTEM_1', 'priority': 1}
            ]
        },
        'assessmentProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Assessment Provider Implementation',
            'description': 'Implementation for assessment service provider',
            'values': [
                {'value': 'TEST_FILESYSTEM_1', 'priority': 1}
            ]
        },
        'authorizationProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Authorization Provider Implementation',
            'description': 'Implementation for authorization service provider',
            'values': [
                {'value': 'TEST_FILESYSTEM_1', 'priority': 1}
            ]
        },
        'learningProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Learning Provider Implementation',
            'description': 'Implementation for learning service provider',
            'values': [
                {'value': 'TEST_FILESYSTEM_1', 'priority': 1}
            ]
        },
        'hierarchyProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Hierarchy Provider Implementation',
            'description': 'Implementation for hierarchy service provider',
            'values': [
                {'value': 'TEST_FILESYSTEM_1', 'priority': 1}
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
                {'value': 'TEST_FILESYSTEM_1', 'priority': 1}
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
                {'value': 'TEST_FILESYSTEM_1', 'priority': 1}
            ]
        },
        'loggingProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Logging Provider Implementation',
            'description': 'Implementation for logging service provider',
            'values': [
                {'value': 'TEST_FILESYSTEM_1', 'priority': 1}
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
                {'value': 'TEST_FILESYSTEM_1', 'priority': 1}
            ]
        },
        'hierarchyProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Hierarchy Provider Implementation',
            'description': 'Implementation for hierarchy service provider',
            'values': [
                {'value': 'TEST_FILESYSTEM_1', 'priority': 1}
            ]
        },
        'authorizationProviderImpl': {
            'syntax': 'STRING',
            'displayName': 'Authorization Provider Implementation',
            'description': 'Implementation for authorization service provider',
            'values': [
                {'value': 'TEST_FILESYSTEM_1', 'priority': 1}
            ]
        },
    }
}
