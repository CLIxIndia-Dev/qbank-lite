################################################
#  LOGGING
################################################
import json
import web

from dlkit_edx.errors import PermissionDenied, InvalidArgument, IllegalState, NotFound
from dlkit_edx.primordium import Id, Type

from pymongo.errors import InvalidId

from records.registry import LOG_ENTRY_RECORD_TYPES

import utilities


TEXT_BLOB_RECORD_TYPE = Type(**LOG_ENTRY_RECORD_TYPES['text-blob'])

urls = (
    "/logs", "LogsList",
    "/logs/(.*)/logentries/(.*)", "LogEntryDetails",
    "/logs/(.*)/logentries", "LogEntriesList",
    "/logs/(.*)", "LogDetails"
)


class LogDetails(utilities.BaseClass):
    """
    Shows details for a specific log.
    api/v2/logging/logs/<log_id>/

    GET, PUT, DELETE
    PUT will update the log. Only changed attributes need to be sent.
    DELETE will remove the log.

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
       PUT {"name" : "a new log"}

    """
    @utilities.format_response
    def DELETE(self, log_id):
        try:
            session._initializer['logm'].delete_log(utilities.clean_id(log_id))

            return web.Accepted()
        except (PermissionDenied, NotFound, InvalidId) as ex:
            utilities.handle_exceptions(ex)
        except IllegalState as ex:
            modified_ex = type(ex)('Log is not empty.')
            utilities.handle_exceptions(modified_ex)

    @utilities.format_response
    def GET(self, log_id):
        try:
            log = session._initializer['logm'].get_log(utilities.clean_id(log_id))
            log = utilities.convert_dl_object(log)

            return log
        except (PermissionDenied, NotFound, InvalidId) as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def PUT(self, log_id):
        try:
            form = session._initializer['logm'].get_log_form_for_update(utilities.clean_id(log_id))

            utilities.verify_at_least_one_key_present(self.data(), ['name', 'description'])

            # should work for a form or json data
            if 'name' in self.data():
                form.display_name = self.data()['name']
            if 'description' in self.data():
                form.description = self.data()['description']

            updated_log = session._initializer['logm'].update_log(form)
            updated_log = utilities.convert_dl_object(updated_log)

            return updated_log
        except (PermissionDenied, KeyError, InvalidArgument, NotFound, InvalidId) as ex:
            utilities.handle_exceptions(ex)


class LogsList(utilities.BaseClass):
    """
    List all available logs.
    api/v2/logging/logs/

    POST allows you to create a new log, requires two parameters:
      * name
      * description

    Alternatively, if you provide an assessment bank ID,
    the log will be orchestrated to have a matching internal identifier.
    The name and description will be set for you, but can optionally be set if
    provided.
      * bankId
      * name (optional)
      * description (optional)

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
      {"name" : "a new log",
       "description" : "this is a test"}

       OR
       {"bankId": "assessment.Bank%3A5547c37cea061a6d3f0ffe71%40cs-macbook-pro"}
    """
    @utilities.format_response
    def GET(self):
        """
        List all available logs
        """
        try:
            logs = session._initializer['logm'].logs
            logs = utilities.extract_items(logs)
            return logs
        except PermissionDenied as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def POST(self):
        """
        Create a new log, if authorized

        """
        try:
            if 'bankId' not in self.data():
                utilities.verify_keys_present(self.data(), ['name', 'description'])
                form = session._initializer['logm'].get_log_form_for_create([])
                finalize_method = session._initializer['logm'].create_log
            else:
                log = session._initializer['logm'].get_log(Id(self.data()['bankId']))
                form = session._initializer['logm'].get_log_form_for_update(log.ident)
                finalize_method = session._initializer['logm'].update_log

            if 'name' in self.data():
                form.display_name = self.data()['name']
            if 'description' in self.data():
                form.description = self.data()['description']

            new_log = utilities.convert_dl_object(finalize_method(form))

            return new_log
        except (PermissionDenied, InvalidArgument, NotFound, KeyError) as ex:
            utilities.handle_exceptions(ex)


class LogEntriesList(utilities.BaseClass):
    """
    Get or add log entry
    api/v2/logging/logs/<log_id>/logentries/

    GET, POST
    GET to view current log entries
    POST to create a new log entry

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
       {"data" : "<JSON string blob, or whatever text blob you want>"}
    """
    @utilities.format_response
    def GET(self, log_id):
        try:
            log = session._initializer['logm'].get_log(utilities.clean_id(log_id))
            entries = log.get_log_entries()

            data = utilities.extract_items(entries)

            return data
        except (PermissionDenied, NotFound) as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def POST(self, log_id):
        try:
            utilities.verify_keys_present(self.data(), ['data'])

            log = session._initializer['logm'].get_log(utilities.clean_id(log_id))
            form = log.get_log_entry_form_for_create([TEXT_BLOB_RECORD_TYPE])

            if isinstance(self.data()['data'], dict):
                blob = json.dumps(self.data()['data'])
            else:
                blob = str(self.data()['data'])

            form.set_text(blob)
            entry = log.create_log_entry(form)

            return utilities.convert_dl_object(entry)
        except (PermissionDenied, InvalidArgument, IllegalState, KeyError) as ex:
            utilities.handle_exceptions(ex)


class LogEntryDetails(utilities.BaseClass):
    """
    Get log entry details
    api/v2/logging/logs/<log_id>/logentries/<entry_id>/

    GET, PUT, DELETE
    PUT to modify an existing log entry (name, score / grade, etc.).
        Include only the changed parameters.
    DELETE to remove the log entry.

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
       {"data" : "foo"}
    """
    @utilities.format_response
    def DELETE(self, log_id, entry_id):
        try:
            log = session._initializer['logm'].get_log(utilities.clean_id(log_id))
            log.delete_log_entry(utilities.clean_id(entry_id))

            return web.Accepted()
        except (PermissionDenied, IllegalState, InvalidId) as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def GET(self, log_id, entry_id):
        try:
            log = session._initializer['logm'].get_log(utilities.clean_id(log_id))
            entry = log.get_log_entry(utilities.clean_id(entry_id))
            entry_map = entry.object_map

            return entry_map
        except (PermissionDenied, NotFound, InvalidId) as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def PUT(self, log_id, entry_id):
        try:
            utilities.verify_at_least_one_key_present(self.data(),
                                                      ['data'])

            log = session._initializer['logm'].get_log(utilities.clean_id(log_id))

            form = log.get_log_entry_form_for_update(utilities.clean_id(entry_id))

            if 'data' in self.data():
                if isinstance(self.data()['data'], dict):
                    blob = json.dumps(self.data()['data'])
                else:
                    blob = str(self.data()['data'])
                form.set_text(blob)

            log.update_log_entry(form)

            entry = log.get_log_entry(utilities.clean_id(entry_id))

            return utilities.convert_dl_object(entry)
        except (PermissionDenied, InvalidArgument, KeyError, InvalidId) as ex:
            utilities.handle_exceptions(ex)


app_logging = web.application(urls, locals())
session = utilities.activate_managers(web.session.Session(app_logging,
                                      web.session.DiskStore('sessions'),
                                      initializer={
                                          'am': None,
                                          'logm': None
                                      }))
