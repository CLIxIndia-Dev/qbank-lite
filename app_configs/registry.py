
MANAGER_PATHS = {

    'service': {
        'ASSESSMENT': ('dlkit.services.assessment.AssessmentManager',
                       'dlkit.services.assessment.AssessmentManager'),
        'AUTHORIZATION': ('dlkit.services.authorization.AuthorizationManager',
                          'dlkit.services.authorization.AuthorizationManager'),
        'REPOSITORY': ('dlkit.services.repository.RepositoryManager',
                       'dlkit.services.repository.RepositoryManager'),
        'LEARNING': ('dlkit.services.learning.LearningManager',
                     'dlkit.services.learning.LearningManager'),
        'LOGGING': ('dlkit.services.logging_.LoggingManager',
                    'dlkit.services.logging_.LoggingManager'),
        'COMMENTING': ('dlkit.services.commenting.CommentingManager',
                       'dlkit.services.commenting.CommentingManager'),
        'RESOURCE': ('dlkit.services.resource.ResourceManager',
                     'dlkit.services.resource.ResourceManager'),
        'GRADING': ('dlkit.services.grading.GradingManager',
                    'dlkit.services.grading.GradingManager')
    },
    'authz_adapter': {
        'ASSESSMENT': ('dlkit.authz_adapter.assessment.managers.AssessmentManager',
                       'dlkit.authz_adapter.assessment.managers.AssessmentProxyManager'),
        'AUTHORIZATION': ('dlkit.authz_adapter.authorization.managers.AuthorizationManager',
                          'dlkit.authz_adapter.authorization.managers.AuthorizationProxyManager'),
        'REPOSITORY': ('dlkit.authz_adapter.repository.managers.RepositoryManager',
                       'dlkit.authz_adapter.repository.managers.RepositoryProxyManager'),
        'LEARNING': ('dlkit.authz_adapter.learning.managers.LearningManager',
                     'dlkit.authz_adapter.learning.managers.LearningProxyManager'),
        'LOGGING': ('dlkit.authz_adapter.logging_.managers.LoggingManager',
                    'dlkit.authz_adapter.logging_.managers.LoggingProxyManager')
    },
    'filesystem': {
        'ASSESSMENT': ('dlkit.mongo.assessment.managers.AssessmentManager',
                       'dlkit.mongo.assessment.managers.AssessmentProxyManager'),
        'AUTHORIZATION': ('dlkit.mongo.authorization.managers.AuthorizationManager',
                          'dlkit.mongo.authorization.managers.AuthorizationProxyManager'),
        'HIERARCHY': ('dlkit.mongo.hierarchy.managers.HierarchyManager',
                      'dlkit.mongo.hierarchy.managers.HierarchyProxyManager'),
        'LEARNING': ('dlkit.mongo.learning.managers.LearningManager',
                     'dlkit.mongo.learning.managers.LearningProxyManager'),
        'LOGGING': ('dlkit.mongo.logging_.managers.LoggingManager',
                    'dlkit.mongo.logging_.managers.LoggingProxyManager'),
        'REPOSITORY': ('dlkit.mongo.repository.managers.RepositoryManager',
                       'dlkit.mongo.repository.managers.RepositoryProxyManager')
    },
    'mongo': {
        'ASSESSMENT': ('dlkit.mongo.assessment.managers.AssessmentManager',
                       'dlkit.mongo.assessment.managers.AssessmentProxyManager'),
        'AUTHORIZATION': ('dlkit.mongo.authorization.managers.AuthorizationManager',
                          'dlkit.mongo.authorization.managers.AuthorizationProxyManager'),
        'HIERARCHY': ('dlkit.mongo.hierarchy.managers.HierarchyManager',
                      'dlkit.mongo.hierarchy.managers.HierarchyProxyManager'),
        'LEARNING': ('dlkit.mongo.learning.managers.LearningManager',
                     'dlkit.mongo.learning.managers.LearningProxyManager'),
        'LOGGING': ('dlkit.mongo.logging_.managers.LoggingManager',
                    'dlkit.mongo.logging_.managers.LoggingProxyManager'),
        'REPOSITORY': ('dlkit.mongo.repository.managers.RepositoryManager',
                       'dlkit.mongo.repository.managers.RepositoryProxyManager')
    },
    'filesystem_adapter': {
        'REPOSITORY': ('dlkit.filesystem.repository.managers.RepositoryManager',
                       'dlkit.filesystem.repository.managers.RepositoryProxyManager')
    }
}
