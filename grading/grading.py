import json
import web
import utilities

import grading_utilities as gutils

urls = (
    "/gradebooks/(.*)/columns/(.*)/summary/?", "GradebookColumnSummary",
    "/gradebooks/(.*)/columns/(.*)/entries/?", "GradeEntriesList",
    "/gradebooks/(.*)/columns/(.*[^/])/?", "GradebookColumnDetails",
    "/gradebooks/(.*)/columns/?", "GradebookColumnsList",
    "/gradebooks/(.*)/entries/(.*)/?", "GradeEntryDetails",
    "/gradebooks/(.*)/entries/?", "GradeEntriesList",
    "/gradebooks/(.*)/gradesystems/(.*)/?", "GradebookGradeSystemDetails",
    "/gradebooks/(.*)/gradesystems/?", "GradebookGradeSystemList",
    "/gradebooks/(.*)/?", "GradebookDetails",
    "/gradebooks/?", "GradebookList"
)


class GradebookList(utilities.BaseClass):
    """
    List all available gradebooks.
    api/v1/grading/gradebooks/

    POST allows you to create a new gradebook, requires two parameters:
      * name
      * description

    Alternatively, if you provide an assessment bank ID,
    the gradebook will be orchestrated to have a matching internal identifier.
    The name and description will be set for you, but can optionally be set if
    provided.
      * bankId
      * name (optional)
      * description (optional)

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
      {"name" : "a new gradebook",
       "description" : "this is a test"}

       OR
       {"bankId": "assessment.Bank%3A5547c37cea061a6d3f0ffe71%40cs-macbook-pro"}
    """
    @utilities.format_response
    def GET(self):
        """
        List all available gradebooks
        """
        try:
            gm = gutils.get_grading_manager()
            gradebooks = utilities.extract_items(gm.gradebooks)
            return gradebooks
        except Exception as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def POST(self):
        """
        Create a new gradebook, if authorized

        """
        try:
            gm = gutils.get_grading_manager()
            form = gm.get_gradebook_form_for_create([])
            data = self.data()

            form = utilities.set_form_basics(form, data)

            new_gradebook = utilities.convert_dl_object(gm.create_gradebook(form))

            if 'aliasId' in data:
                gm.alias_bank(utilities.clean_id(json.loads(new_gradebook)['id']),
                              utilities.clean_id(data['aliasId']))

            return new_gradebook
        except Exception as ex:
            utilities.handle_exceptions(ex)


class GradebookDetails(utilities.BaseClass):
    """
    Shows details for a specific gradebook.
    api/v1/grading/gradebooks/<gradebook_id>/

    GET, PUT, DELETE
    PUT will update the gradebook. Only changed attributes need to be sent.
    DELETE will remove the gradebook.

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
       PUT {"name" : "a new gradebook"}
    """
    @utilities.format_response
    def GET(self, gradebook_id):
        try:
            gm = gutils.get_grading_manager()
            grading_gradebook = gm.get_gradebook(utilities.clean_id(gradebook_id))
            gradebook = utilities.convert_dl_object(grading_gradebook)
            return gradebook
        except Exception as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def PUT(self, gradebook_id):
        try:
            gm = gutils.get_grading_manager()
            data = self.data()

            form = gm.get_gradebook_form_for_update(utilities.clean_id(gradebook_id))

            utilities.verify_at_least_one_key_present(self.data(), ['name', 'description', 'displayName'])

            form = utilities.set_form_basics(form, data)
            updated_gradebook = gm.update_gradebook(form)

            if 'aliasId' in data:
                gm.alias_bank(updated_gradebook.ident, utilities.clean_id(data['aliasId']))

            gradebook = utilities.convert_dl_object(updated_gradebook)
            return gradebook
        except Exception as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def DELETE(self, gradebook_id):
        try:
            gm = gutils.get_grading_manager()
            data = gm.delete_gradebook(utilities.clean_id(gradebook_id))
            return utilities.success()
        except Exception as ex:
            utilities.handle_exceptions(ex)


class GradebookGradeSystemList(utilities.BaseClass):
    """
    Get or add gradesystems to a gradebook
    api/v1/grading/gradebooks/<gradebook_id>/gradesystems/

    GET, POST
    GET to view current gradesystems.
    POST to create a new gradesystem

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
       {"name" : "Letters", "description": "Letter grades A - F"}
    """
    @utilities.format_response
    def GET(self, gradebook_id):
        try:
            gm = gutils.get_grading_manager()
            gradebook = gm.get_gradebook(utilities.clean_id(gradebook_id))

            grading_grade_systems = gradebook.get_grade_systems()
            grade_systems = utilities.extract_items(grading_grade_systems)
            return grade_systems
        except Exception as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def POST(self, gradebook_id):
        try:
            gm = gutils.get_grading_manager()
            gradebook = gm.get_gradebook(utilities.clean_id(gradebook_id))

            form = gradebook.get_grade_system_form_for_create([])
            data = self.data()

            form = utilities.set_form_basics(form, data)

            check_scores = True

            if 'basedOnGrades' in data:
                form.set_based_on_grades(bool(data['basedOnGrades']))
                if data['basedOnGrades']:
                    check_scores = False

            if check_scores:
                gutils.check_numeric_score_inputs(data)

                form.set_highest_numeric_score(float(data['highestNumericScore']))
                form.set_lowest_numeric_score(float(data['lowestNumericScore']))
                form.set_numeric_score_increment(float(data['numericScoreIncrement']))

            grade_system = gradebook.create_grade_system(form)

            if not check_scores:
                gutils.check_grade_inputs(data)
                gutils.add_grades_to_grade_system(gradebook,
                                                   grade_system,
                                                   data)

            new_grade_system = utilities.convert_dl_object(gradebook.get_grade_system(grade_system.ident))

            return new_grade_system
        except Exception as ex:
            try:
                gradebook.delete_grade_system(grade_system.ident)
            except NameError:
                pass
            utilities.handle_exceptions(ex)


class GradebookGradeSystemDetails(utilities.BaseClass):
    """
    Get grade system details
    api/v1/grading/gradebooks/<gradebook_id>/gradesystems/<gradesystem_id>/

    GET, PUT, DELETE
    PUT to modify an existing grade system (name or settings). Include only the changed parameters.
    DELETE to remove the grade system.

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
       {"name" : "an updated item"}
    """
    @utilities.format_response
    def GET(self, gradebook_id, gradesystem_id):
        try:
            gm = gutils.get_grading_manager()
            gradebook = gm.get_gradebook(utilities.clean_id(gradebook_id))
            grading_grade_system = gradebook.get_grade_system(utilities.clean_id(gradesystem_id))
            grade_system = utilities.convert_dl_object(grading_grade_system)
            return grade_system
        except Exception as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def PUT(self, gradebook_id, gradesystem_id):
        try:
            gm = gutils.get_grading_manager()
            data = self.data()
            utilities.verify_at_least_one_key_present(data,
                                                      ['name', 'displayName', 'description', 'basedOnGrades',
                                                       'grades', 'highestScore', 'lowestScore',
                                                       'scoreIncrement'])
            gradebook = gm.get_gradebook(utilities.clean_id(gradebook_id))
            grade_system = gradebook.get_grade_system(utilities.clean_id(gradesystem_id))
            form = gradebook.get_grade_system_form_for_update(grade_system.ident)
            form = utilities.set_form_basics(form, data)

            if 'basedOnGrades' in data:
                # do this first, so methods below work
                form.set_based_on_grades(bool(data['basedOnGrades']))

                if data['basedOnGrades']:
                    # clear out the numeric score fields
                    form.clear_highest_numeric_score()
                    form.clear_lowest_numeric_score()
                    form.clear_numeric_score_increment()
                else:
                    # clear out grades
                    for grade in grade_system.get_grades():
                        gradebook.delete_grade(grade.ident)

            if (grade_system.is_based_on_grades() and
                    'grades' in data):
                # user wants to update the grades
                # here, wipe out all previous grades and over-write
                gutils.check_grade_inputs(data)
                if len(data['grades']) > 0:
                    for grade in grade_system.get_grades():
                        gradebook.delete_grade(grade.ident)
                    gutils.add_grades_to_grade_system(gradebook,
                                                      grade_system,
                                                      data)

            score_inputs = ['highestScore', 'lowestScore', 'scoreIncrement']
            if (not grade_system.is_based_on_grades() and
                    any(i in data for i in score_inputs)):
                if 'highestScore' in data:
                    form.set_highest_numeric_score(float(data['highestScore']))

                if 'lowestScore' in data:
                    form.set_lowest_numeric_score(float(data['lowestScore']))

                if 'scoreIncrement' in data:
                    form.set_numeric_score_increment(float(data['scoreIncrement']))

            gradebook.update_grade_system(form)

            grade_system = utilities.convert_dl_object(gradebook.get_grade_system(grade_system.ident))
            return grade_system
        except Exception as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def DELETE(self, gradebook_id, gradesystem_id):
        try:
            gm = gutils.get_grading_manager()
            gradebook = gm.get_gradebook(utilities.clean_id(gradebook_id))
            data = gradebook.delete_grade_system(utilities.clean_id(gradesystem_id))
            return utilities.success()
        except Exception as ex:
            utilities.handle_exceptions(ex)


class GradebookColumnsList(utilities.BaseClass):
    """
    Get or add column to a gradebook
    api/v1/grading/gradebooks/<gradebook_id>/columns/

    GET, POST
    GET to view current columns.
    POST to create a new column

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
       {"gradeSystemId" : "grading.GradeSystem%3A123%40MIT-ODL"}
    """
    @utilities.format_response
    def GET(self, gradebook_id):
        try:
            gm = gutils.get_grading_manager()
            gradebook = gm.get_gradebook(utilities.clean_id(gradebook_id))
            grading_columns = gradebook.get_gradebook_columns()

            columns = utilities.extract_items(grading_columns)
            return columns
        except Exception as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def POST(self, gradebook_id):
        try:
            gm = gutils.get_grading_manager()
            gradebook = gm.get_gradebook(utilities.clean_id(gradebook_id))

            data = self.data()
            utilities.verify_keys_present(data, ['gradeSystemId'])
            gutils.validate_grade_system_exists(gradebook, utilities.clean_id(data['gradeSystemId']))

            form = gradebook.get_gradebook_column_form_for_create([])
            form = utilities.set_form_basics(form, data)
            form.set_grade_system(utilities.clean_id(data['gradeSystemId']))

            column = utilities.convert_dl_object(gradebook.create_gradebook_column(form))

            return column
        except Exception as ex:
            utilities.handle_exceptions(ex)


class GradebookColumnDetails(utilities.BaseClass):
    """
    Get grade column details
    api/v1/grading/gradebooks/<gradebook_id>/columns/<column_id>/

    GET, PUT, DELETE
    PUT to modify an existing gradebook column (name or gradeSystemId).
        Include only the changed parameters.
    DELETE to remove the gradebook column.

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
       {"name" : "an updated item"}
    """
    @utilities.format_response
    def GET(self, gradebook_id, column_id):
        try:
            gm = gutils.get_grading_manager()
            gradebook = gm.get_gradebook(utilities.clean_id(gradebook_id))
            grading_gradebook_column = gradebook.get_gradebook_column(utilities.clean_id(column_id))
            gradebook_column = utilities.convert_dl_object(grading_gradebook_column)
            return gradebook_column
        except Exception as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def PUT(self, gradebook_id, column_id):
        try:
            gm = gutils.get_grading_manager()
            data = self.data()
            utilities.verify_at_least_one_key_present(data,
                                                   ['name', 'displayName', 'description', 'gradeSystemId'])

            gradebook = gm.get_gradebook(utilities.clean_id(gradebook_id))
            gradebook_column = gradebook.get_gradebook_column(utilities.clean_id(column_id))

            form = gradebook.get_gradebook_column_form_for_update(gradebook_column.ident)
            form = utilities.set_form_basics(form, data)
            if 'gradeSystemId' in data:
                form.set_grade_system(utilities.clean_id(data['gradeSystemId']))

            gradebook.update_gradebook_column(form)

            gradebook_column = utilities.convert_dl_object(gradebook.get_gradebook_column(gradebook_column.ident))
            return gradebook_column
        except Exception as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def DELETE(self, gradebook_id, column_id):
        try:
            gm = gutils.get_grading_manager()
            gradebook = gm.get_gradebook(utilities.clean_id(gradebook_id))
            data = gradebook.delete_gradebook_column(utilities.clean_id(column_id))
            return utilities.success()
        except Exception as ex:
            utilities.handle_exceptions(ex)


class GradeEntriesList(utilities.BaseClass):
    """
    Get or add grade entry to a gradebook column
    api/v1/grading/gradebooks/<gradebook_id>/columns/<column_id>/entries

    OR view all entries in a gradebook
    api/v1/grading/gradebooks/<gradebook_id>/entries

    GET, POST
    GET to view current grade entries (in whole gradebook or single gradebook column).
    POST to create a new grade entry (only to a specific gradebook)

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
       {"grade" : "grading.Grade%3A123%40MIT-ODL"}
    """
    @utilities.format_response
    def GET(self, gradebook_id, column_id=None):
        try:
            gm = gutils.get_grading_manager()
            gradebook = gm.get_gradebook(utilities.clean_id(gradebook_id))
            if column_id is None:
                grading_entries = gradebook.get_grade_entries()
            else:
                grading_entries = gradebook.get_grade_entries_for_gradebook_column(utilities.clean_id(column_id))

            entries = utilities.extract_items(grading_entries)
            return entries
        except Exception as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def POST(self, gradebook_id, column_id=None):
        try:
            gm = gutils.get_grading_manager()

            data = self.data()
            utilities.verify_at_least_one_key_present(data,
                                                   ['grade', 'score', 'ignoredForCalculations'])
            utilities.verify_keys_present(data, ['resourceId'])
            if column_id is None:
                utilities.verify_keys_present(data, ['columnId'])
                column_id = data['columnId']

            gradebook = gm.get_gradebook(utilities.clean_id(gradebook_id))
            column = gradebook.get_gradebook_column(utilities.clean_id(column_id))

            gutils.validate_score_and_grades_against_system(column.get_grade_system(),
                                                             data)
            form = gradebook.get_grade_entry_form_for_create(column.ident,
                                                             utilities.clean_id(data['resourceId']),
                                                             [])
            form = utilities.set_form_basics(form, data)
            if 'ignoredForCalculations' in data:
                form.set_ignored_for_calculations(bool(data['ignoredForCalculations']))

            if 'grade' in data:
                form.set_grade(utilities.clean_id(data['grade']))

            if 'score' in data:
                form.set_score(float(data['score']))

            entry = utilities.convert_dl_object(gradebook.create_grade_entry(form))

            return entry
        except Exception as ex:
            utilities.handle_exceptions(ex)

class GradeEntryDetails(utilities.BaseClass):
    """
    Get grade entry details
    api/v1/grading/gradebooks/<gradebook_id>/entries/<entry_id>/

    GET, PUT, DELETE
    PUT to modify an existing grade entry (name, score / grade, etc.).
        Include only the changed parameters.
    DELETE to remove the grade entry.

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
       {"score" : 98.2}
    """
    @utilities.format_response
    def GET(self, gradebook_id, entry_id):
        try:
            gm = gutils.get_grading_manager()
            gradebook = gm.get_gradebook(utilities.clean_id(gradebook_id))
            grading_entry = gradebook.get_grade_entry(utilities.clean_id(entry_id))
            entry = utilities.convert_dl_object(grading_entry)
            return entry
        except Exception as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def PUT(self, gradebook_id, entry_id):
        try:
            gm = gutils.get_grading_manager()
            data = self.data()
            utilities.verify_at_least_one_key_present(data,
                                                   ['name', 'displayName', 'description', 'grade',
                                                    'score', 'ignoredForCalculations'])

            gradebook = gm.get_gradebook(utilities.clean_id(gradebook_id))
            entry = gradebook.get_grade_entry(utilities.clean_id(entry_id))
            grade_system = entry.get_gradebook_column().get_grade_system()

            gutils.validate_score_and_grades_against_system(grade_system, data)

            form = gradebook.get_grade_entry_form_for_update(entry.ident)
            form = utilities.set_form_basics(form, data)
            if 'grade' in data:
                form.set_grade(utilities.clean_id(data['grade']))

            if 'score' in data:
                form.set_score(float(data['score']))

            if 'ignoredForCalculations' in data:
                form.set_ignored_for_calculations(bool(data['ignoredForCalculations']))

            gradebook.update_grade_entry(form)

            entry = utilities.convert_dl_object(gradebook.get_grade_entry(entry.ident))
            return entry
        except Exception as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def DELETE(self, gradebook_id, entry_id):
        try:
            gm = gutils.get_grading_manager()
            gradebook = gm.get_gradebook(utilities.clean_id(gradebook_id))
            data = gradebook.delete_grade_entry(utilities.clean_id(entry_id))
            return utilities.success()
        except Exception as ex:
            utilities.handle_exceptions(ex)


class GradebookColumnSummary(utilities.BaseClass):
    """
    Get grade system details
    api/v1/grading/gradebooks/<gradebook_id>/columns/<column_id>/summary/

    GET

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'
    """
    @utilities.format_response
    def GET(self, gradebook_id, column_id):
        try:
            gm = gutils.get_grading_manager()
            gradebook = gm.get_gradebook(utilities.clean_id(gradebook_id))
            if gradebook.get_grade_entries_for_gradebook_column(utilities.clean_id(column_id)).available() > 0:
                gradebook_column_summary = gradebook.get_gradebook_column_summary(utilities.clean_id(column_id))
                gradebook_column_summary_map = {
                    'mean': gradebook_column_summary.get_mean(),
                    'median': gradebook_column_summary.get_median(),
                    'mode': gradebook_column_summary.get_mode(),
                    'rootMeanSquared': gradebook_column_summary.get_rms(),
                    'standardDeviation': gradebook_column_summary.get_standard_deviation(),
                    'sum': gradebook_column_summary.get_sum()
                }
            else:
                gradebook_column_summary_map = {
                    'mean': 0.0,
                    'median': 0.0,
                    'mode': 0.0,
                    'rootMeanSquared': 0.0,
                    'standardDeviation': 0.0,
                    'sum': 0.0
                }

            return gradebook_column_summary_map
        except Exception as ex:
            utilities.handle_exceptions(ex)

app_grading = web.application(urls, locals())
