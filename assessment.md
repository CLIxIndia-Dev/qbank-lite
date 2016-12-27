# Assessment Service

## Headers

QBank uses various headers to represent the user and settings. They are outlined below.

`x-api-proxy`: The username or a sessionId (from unplatform).
`x-api-locale`: The current language locale (`en`, `hi`, and `te` currently supported), for questions that
                support this feature. This is used for both setting language (for `POST` or `PUT` of
                language fields), as well as display of the question text (on `GET` of questions).
                Note that for multi-language fields, only **one** value for a given language type
                is supported. Providing a new value automatically replaces the previous value, with
                the matching language code. Note that for `POST` or `PUT` operations you can
                provide either the new text + `x-api-locale`, or just provide the entire
                `DisplayText` object, which specifies the language values:
                {text: 'टेक्स्ट',
                 languageTypeId: '639-2%3AHIN%40ISO',
                 formatTypeId: 'TextFormats%3APLAIN%40okapia.net',
                 scriptTypeId: '15924%3ADEVA%40ISO'}
                {text: 'టెక్స్ట్',
                 languageTypeId: '639-2%3ATEL%40ISO',
                 formatTypeId: 'TextFormats%3APLAIN%40okapia.net',
                 scriptTypeId: '15924%3ATELU%40ISO'}
                {text: 'text',
                 languageTypeId: '639-2%3AENG%40ISO',
                 formatTypeId: 'TextFormats%3APLAIN%40okapia.net',
                 scriptTypeId: '15924%3ALATN%40ISO'}

## URLs

The following are in the schema of `url` -> `sub-heading`

```
/banks/(.*)/assessmentsoffered/(.*)/assessmentstaken -> AssessmentsTaken
/banks/(.*)/assessmentsoffered/(.*)/results -> AssessmentOfferedResults
/banks/(.*)/assessmentsoffered/(.*) -> AssessmentOfferedDetails
/banks/(.*)/assessmentstaken/(.*)/questions/(.*)/qti -> AssessmentTakenQuestionQTIDetails
/banks/(.*)/assessmentstaken/(.*)/questions/(.*)/status -> AssessmentTakenQuestionStatus
/banks/(.*)/assessmentstaken/(.*)/questions/(.*)/submit -> AssessmentTakenQuestionSubmit
/banks/(.*)/assessmentstaken/(.*)/questions/(.*) -> AssessmentTakenQuestionDetails
/banks/(.*)/assessmentstaken/(.*)/questions -> AssessmentTakenQuestions
/banks/(.*)/assessmentstaken/(.*)/finish -> FinishAssessmentTaken
/banks/(.*)/assessmentstaken/(.*) -> AssessmentTakenDetails
/banks/(.*)/assessments/(.*)/assessmentsoffered -> AssessmentsOffered
/banks/(.*)/assessments/(.*)/items/(.*) -> AssessmentItemDetails
/banks/(.*)/assessments/(.*)/items -> AssessmentItemsList
/banks/(.*)/assessments/(.*) -> AssessmentDetails
/banks/(.*)/assessments -> AssessmentsList
/banks/(.*)/items/(.*)/videoreplacement -> ItemVideoTagReplacement
/banks/(.*)/items/(.*)/qti -> ItemQTIDetails
/banks/(.*)/items/(.*) -> ItemDetails
/banks/(.*)/items -> ItemsList
/banks/(.*) -> AssessmentBankDetails
/banks -> AssessmentBanksList
/hierarchies/roots/(.*) -> AssessmentHierarchiesRootDetails
/hierarchies/roots -> AssessmentHierarchiesRootsList
/hierarchies/nodes/(.*)/children -> AssessmentHierarchiesNodeChildrenList
/hierarchies/nodes/(.*) -> AssessmentHierarchiesNodeDetails
```

### AssessmentsTaken

Get or create an assessment taken, for a specific assessment offered.
`/api/v1/assessment/banks/<bank_id>/assessmentsoffered/<offered_id>/assessmentstaken`

#### GET

url arguments (required):
  - bank_id. Example: assessment.Bank%3A57b952b7ed849b7a42085962%40ODL.MIT.EDU
  - offered_id. Example: assessment.AssessmentOffered%3A57b952b7ed849b7a42085962%40ODL.MIT.EDU

returns:
  - list of `AssessmentOffered`s.

#### POST

This creates an `AssessmentTaken` record for the given `x-api-proxy` username. It links a specific
user action to an `AssessmentOffered`, and its `id` needs to be used to retrieve questions and submit
responses to questions.

url arguments (required):
  - bank_id. Example: assessment.Bank%3A57b952b7ed849b7a42085962%40ODL.MIT.EDU
  - offered_id. Example: assessment.AssessmentOffered%3A57b952b7ed849b7a42085962%40ODL.MIT.EDU

headers (expected):
  - x-api-proxy. Student username (will be parsed into an OSID `agent` on the server-side). Should be
                 in the format student@clix.edu, or some unplatform sessionId.

returns:
  - `AssessmentTaken` JSON object.

### AssessmentOfferedResults

Get the class-wide results for a specific `AssessmentOffered`. Not currently used in CLIx, this
aggregates all the `AssessmentTaken`s and returns the questions + responses.
`/api/v1/assessment/banks/<bank_id>/assessmentsoffered/<offered_id>/results`

#### GET

url parameters (optional):
  - None currently supported

returns:
  - list of `AssessmentTaken`s.

### AssessmentOfferedDetails

Get, edit, or delete a specific `AssessmentOffered`.
`/api/v1/assessment/banks/<bank_id>/assessmentsoffered/<offered_id>`

#### DELETE

This requires that all the `AssessmentTaken`s associated with this `AssessmentOffered` are deleted
from the system first. Currently, no convenience method exists to do this in bulk -- separate
calls are required to the `AssessmentTakenDetails` endpoint.

returns:
  - 202.

#### GET

url parameters (optional):
  - None currently supported

returns:
  - `AssessmentOffered` JSON object.

#### PUT

This is not a "replace all attributes" endpoint, but rather a selective-replace endpoint.
Any attributes passed in are replaced, without modifying or deleting the other attributes.

form data (optional):
  - duration. Length of time the `assessment` will be valid for, after the student "starts" it.
              Expected format is a dictionary with, valid keys being: `days`, `hours`, `minutes`,
              `seconds`, `milliseconds`, `microseconds`.
  - gradeSystem. Corresponding `GradeSystem` provided by the `grading` service. Not currently
                 configured or used for CLIx.
  - level. A `level` or `gradeId` corresponding to the expected grade the `AssessmentOffered` targets.
           Not currently used for CLIx.
  - startTime. A dictionary representing when the `assessment` is open to students. Defaults to
               `now`. Valid keys include: `year`, `month`, `day`, `hour`, `minute`, `second`,
               `microsecond`.
  - scoreSystem. How the `assessment` will be scored. Not currently used by CLIx.
  - reviewOptions. A nested dictionary with two valid keys, `whetherCorrect` and `solution`, this
                   configuration defines if or when students will be able to see feedback.
      - whetherCorrect. Determines when a student can see if their response is correct or not.
                        This is a dictionary of four keys, each set to `True` or `False`. Default
                        for all keys is `True`. The keys are: `duringAttempt`, `afterAttempt`,
                        `beforeDeadline`, and `afterDeadline`.
      - solution. If available in the `item` definition, defines if a student can see the authored
                  solution. This is a dictionary of four keys, each set to `True` or `False`. Default
                  for all keys is `True`. The keys are: `duringAttempt`, `afterAttempt`,
                  `beforeDeadline`, and `afterDeadline`.
  - maxAttempts. The maximum number of times a student can try the same question. This is applied
                 against all questions in the assessment.
  - nOfM. The number of questions (`n`) out of all the questions (`M`) in the assessment, that
          the student is expected to complete for a passing grade.

returns:
  - the updated `AssessmentOffered` JSON object.

### AssessmentTakenQuestionQTIDetails

Returns the specified question in QTI XML format
`/api/v1/assessment/banks/<bank_id>/assessmentstaken/<taken_id>/questions/<question_id>/qti`

#### GET

url parameters (optional):
  - None currently supported

headers (expected):
  - x-api-proxy. Student username (will be parsed into an OSID `agent` on the server-side). Should be
                 in the format student@clix.edu, or some unplatform sessionId.
  - x-api-locale. For multi-language questions, the text will be returned in the specified language.

returns:
  - XML document.

### AssessmentTakenQuestionStatus

Gets the current status of a question in a taken -- responded to or not, correct or incorrect
response (if applicable)
`/api/v1/assessment/banks/<bank_id>/assessmentstaken/<taken_id>/questions/<question_id>/status`

#### GET

url parameters (optional):
  - None currently supported

headers (expected):
  - x-api-proxy. Student username (will be parsed into an OSID `agent` on the server-side). Should be
                 in the format student@clix.edu, or some unplatform sessionId.

returns:
  - object with `responded` key. If `responded` is `True`, will also return a `correct` key
    reflecting the validity of the response.

### AssessmentTakenQuestionSubmit

Submits a student response for the specified question
Returns correct or not
Does NOTHING to flag if the section is done or not...i.e. does not `finish` the assessment.
`/api/v1/assessment/banks/<bank_id>/assessmentstaken/<taken_id>/questions/<question_id>/submit`

#### POST

The exact data required for this endpoint depends on the type of question being responded to.

headers (expected):
  - x-api-proxy. Student username (will be parsed into an OSID `agent` on the server-side). Should be
                 in the format student@clix.edu, or some unplatform sessionId.
  - x-api-locale. For text submissions, this will be used to correctly label the response language.

form data for file submission type questions (moveable words sandbox, audio record tool, and generic
file upload):
  - type. One of the following values:
            `answer-type%3Aqti-upload-interaction-audio%40ODL.MIT.EDU`,
            `answer-type%3Aqti-upload-interaction-generic%40ODL.MIT.EDU`,
            `answer-type%3Aqti-order-interaction-mw-sandbox%40ODL.MIT.EDU`
  - submission. The file the student is submitting as their response.

form data for multiple choice (single or multi response), reflection, moveable words sentence,
or image sequence questions:
  - type. One of the following values:
            `answer-type%3Aqti-choice-interaction%40ODL.MIT.EDU`,
            `answer-type%3Aqti-choice-interaction-multi-select%40ODL.MIT.EDU`,
            `answer-type%3Aqti-choice-interaction-survey%40ODL.MIT.EDU`,
            `answer-type%3Aqti-choice-interaction-multi-select-survey%40ODL.MIT.EDU`,
            `answer-type%3Aqti-order-interaction-mw-sentence%40ODL.MIT.EDU`,
            `answer-type%3Aqti-order-interaction-object-manipulation%40ODL.MIT.EDU`
  - choiceIds. List of `choiceId`s. Order matters for moveable words sentence, but not for the others.

form data for short response / text answer:
  - type. `answer-type%3Aqti-extended-text-interaction%40ODL.MIT.EDU`
  - text. The text submission from the student.

form data for numeric response:
  - type. `answer-type%3Aqti-numeric-response%40ODL.MIT.EDU`
  - <region>. For each blank area in the question, the corresponding <region> key must include
              the student response as a string value. For example, this could be {RESPONSE_1: '57'}

form data for fill-in-the-blank:
  - type. `answer-type%3Aqti-inline-choice-interaction-mw-fill-in-the-blank%40ODL.MIT.EDU`
  - inlineRegions. A dictionary mapping with keys equal to the response regions of the
                   question, i.e. `RESPONSE_1`. Each value is also a dictionary with
                   a key `choiceIds`, a list of `choiceId` values the student has
                   responded with. Should be of length 1. {RESPONSE_1: {choiceIds: ['123']}}

returns:
  - a dictionary with potentially three keys. `correct` indicates the status of the student
    response. `feedback`, if available in the question, provides authored feedback.
    `confusedLearningObjectiveIds`, if available in the question, indicates a learning outcome
    corresponding to an incorrect response.

### AssessmentTakenQuestionDetails

Returns the specified question
`/api/v1/assessment/banks/<bank_id>/assessmentstaken/<taken_id>/questions/<question_id>`

#### GET

url parameters (optional):
  - None currently supported

headers (expected):
  - x-api-proxy. Student username (will be parsed into an OSID `agent` on the server-side). Should be
                 in the format student@clix.edu, or some unplatform sessionId.
  - x-api-locale. For multi-language questions, the text will be returned in the specified language.

returns:
  - question JSON object with `responded` key. If `responded` is `True`, will also return a `correct` key
    reflecting the validity of the latest response.

### AssessmentTakenQuestions

Returns all of the questions for a given assessment taken.
Assumes that only one section per assessment.
`/api/v1/assessment/banks/<bank_id>/assessmentstaken/<taken_id>/questions`

#### GET

url parameters (optional):
  - qti. Get QTI versions of all questions, if available.

headers (expected):
  - x-api-proxy. Student username (will be parsed into an OSID `agent` on the server-side). Should be
                 in the format student@clix.edu, or some unplatform sessionId.
  - x-api-locale. For multi-language questions, the text will be returned in the specified language.

returns:
  - list of question JSON objects. Does not include `responded` or `correct` status.

### FinishAssessmentTaken

"finish" the `assessment` to indicate that student has ended his/her attempt. This prevents
students from submitting answers to any questions, and also sets a timestamp on the server
indicating when the student finished the `assessment`.
`/api/v1/assessment/banks/<bank_id>/assessmentstaken/<taken_id>/finish`

#### POST

headers (expected):
  - x-api-proxy. Student username (will be parsed into an OSID `agent` on the server-side). Should be
                 in the format student@clix.edu, or some unplatform sessionId.

returns:
  - dictionary of {success: True}

### AssessmentTakenDetails

Get a single taken instance of an assessment. Useful mainly for clean-up and administration
of individual student records / deleting `AssessmentOffered`s.
`/api/v1/assessment/banks/<bank_id>/assessmentstaken/<taken_id>`

#### DELETE

returns:
  - 202.

#### GET

returns:
  - `AssessmentTaken` JSON object.

### AssessmentsOffered

Get or create `offered`s of an `assessment`
`/api/v1/assessment/banks/<bank_id>/assessments/<assessment_id>/assessmentsoffered`

#### GET

url parameters (optional):
  - None currently supported

returns:
  - list of `AssessmentOffered` JSON objects.

#### POST

Note that currently, you can only create an offered if an assessment has items attached to it.

form data (optional):
  - duration. Length of time the `assessment` will be valid for, after the student "starts" it.
              Expected format is a dictionary with, valid keys being: `days`, `hours`, `minutes`,
              `seconds`, `milliseconds`, `microseconds`.
  - gradeSystem. Corresponding `GradeSystem` provided by the `grading` service. Not currently
                 configured or used for CLIx.
  - level. A `level` or `gradeId` corresponding to the expected grade the `AssessmentOffered` targets.
           Not currently used for CLIx.
  - startTime. A dictionary representing when the `assessment` is open to students. Defaults to
               `now`. Valid keys include: `year`, `month`, `day`, `hour`, `minute`, `second`,
               `microsecond`.
  - scoreSystem. How the `assessment` will be scored. Not currently used by CLIx.
  - reviewOptions. A nested dictionary with two valid keys, `whetherCorrect` and `solution`, this
                   configuration defines if or when students will be able to see feedback.
      - whetherCorrect. Determines when a student can see if their response is correct or not.
                        This is a dictionary of four keys, each set to `True` or `False`. Default
                        for all keys is `True`. The keys are: `duringAttempt`, `afterAttempt`,
                        `beforeDeadline`, and `afterDeadline`.
      - solution. If available in the `item` definition, defines if a student can see the authored
                  solution. This is a dictionary of four keys, each set to `True` or `False`. Default
                  for all keys is `True`. The keys are: `duringAttempt`, `afterAttempt`,
                  `beforeDeadline`, and `afterDeadline`.
  - maxAttempts. The maximum number of times a student can try the same question. This is applied
                 against all questions in the assessment.
  - nOfM. The number of questions (`n`) out of all the questions (`M`) in the assessment, that
          the student is expected to complete for a passing grade.

### AssessmentItemDetails

Remove a single `item` from the specified `assessment`.
Note that this does **not** delete the `item` from the system, it only "unlinks" the
`item` from the `assessment`.
`/api/v1/assessment/banks/<bank_id>/assessments/<assessment_id>/items/<item_id>`

#### DELETE

returns:
  - 202.

### AssessmentItemsList

Get or link items in an assessment
`/api/v1/assessment/banks/<bank_id>/assessments/<assessment_id>/items`

#### GET

url parameters (optional):
  - qti. Get the `item`s with a `qti` key that includes the QTI 1 XML representation of the `item`.

returns:
  - list of `Item` JSON objects.

#### POST

This is a full-replace endpoint, and will replace the current list of `item`s in the assessment.
This can also be used to re-order `item`s.

form data (required):
  - itemIds. List of `item` IDs, in the desired final order.

returns:
  - list of `item` JSON objects.

### AssessmentDetails

Get, edit, or delete a specific `assessment`
`/api/v1/assessment/banks/<bank_id>/assessments/<assessment_id>`

#### DELETE

returns:
  - 202.

#### GET

url parameters (optional):
  - None currently supported

returns:
  - `Assessment` JSON object.

#### PUT

Note that the form data will differ for multi-language `assessment`s. Older `assessment`s will not
have this kind of support. You can identify if an `assessment` is multi-language by looking at
its `recordTypeIds` property. If it has values like `osid-object%3Amulti-language%40ODL.MIT.EDU`,
then you need to use the multi-language form values specified below.

form data (single-language):
  - name. A name / title for the `assessment` that will help authors identify it in a UI. Limited
          to 256 characters. Will be set to the default language of `en`.
  - description. A longer text field to describe the `assessment`. Limited to 1024 characters.
                 Will be set to the default language of `en`.
  - genusTypeId. A string field useful for UIs in differentiating between `assessment` types. Not
                 specifically used in CLIx.
  - itemIds. A list of `item` IDs to appear in the `assessment`.

headers (multi-language):
  - x-api-locale. If set, the text fields provided will be declared as the specified language.

form data (multi-language):
  - name. A new language name / title for the `assessment`.
  - description. A new language description for the `assessment`.
  - editName. To replace the name in a specific language, you can include either just the text
              and declare the `x-api-locale` header, or you can provide the entire
              `DisplayText` object.
  - removeName. To specify an existing language value to remove. Note that this looks for
                a string + language setting match, not just the language setting match.
  - editDescription. To replace the description in a specific language, you can include either
                     just the text and declare the `x-api-locale` header, or you can provide
                     the entire `DisplayText` object.
  - removeDescription. To specify an existing language value to remove. Note that this looks for
                       a string + language setting match, not just the language setting match.
  - genusTypeId. A string field useful for UIs in differentiating between `assessment` types. Not
                 specifically used in CLIx.

returns:
  - `Assessment` JSON object. Note that this does **not** include the `item`s.

### AssessmentsList

Get a list of all `assessment`s in the specified `bank`. Also create an `assessment`.
`/api/v1/assessment/banks/<bank_id>/assessments`

#### GET

url parameters (optional):
  - None currently supported

returns:
  - list of `Assessment` JSON objects.

#### POST

Note that all new `assessment`s by default support multi-language. We no longer support
creation of new, single-language `assessment`s. Also, note that on creation, we only allow
(given the CLIx workflow) a single `name` or `description`, set to the language defined
in `x-api-locale` or in the `DisplayText` object.

headers (optional):
  - x-api-locale. If set, the text fields provided will be declared as the specified language.

form data (optional):
  - name. A new language name / title for the `assessment`.
  - description. A new language description for the `assessment`.
  - genusTypeId. A string field useful for UIs in differentiating between `assessment` types. Not
                 specifically used in CLIx.

returns:
  - `Assessment` JSON object. Note that this does **not** include the `item`s.

### ItemVideoTagReplacement

Note that this workflow was used to script some processes that would be
replicated *differently* in an interactive tool, and so is not included here.

`/api/v1/assessment/banks/<bank_id>/items/<item_id>/videoreplacement`

#### POST

form data (required):
  - omitted for now

### ItemQTIDetails

Get QTI 1 XML version of an `item`
`/api/v1/assessment/banks/<bank_id>/items/<item_id>/qti`

#### GET

url parameters (optional):
  - None currently supported

returns:
  - `Item` JSON object.

### ItemDetails

Get, edit, or delete a single `item`
`/api/v1/assessment/banks/<bank_id>/assessments/<assessment_id>/items/<item_id>`

#### DELETE

returns:
  - 202.

#### GET

url parameters (optional):
  - None currently supported

returns:
  - `Item` JSON object. For convenience, wrong answers are also included in the response.

#### PUT

Note that the form data will differ for multi-language `item`s. Older `item`s will not
have this kind of support. You can identify if an `item` (or question, answer) is multi-language
by looking at its `recordTypeIds` property. If it has values like
`osid-object%3Amulti-language%40ODL.MIT.EDU`, then you need to use the multi-language form
values specified below.

Also, as with submitting responses to questions, the form data for each type of `item` differs.

form data (single language, shared across all `item` types, optional):
  - name. A name / title for the `item` that will help authors identify it in a UI. Limited
          to 256 characters. Will be set to the default language of `en`.
  - description. A longer text field to describe the `item`. Limited to 1024 characters.
                 Will be set to the default language of `en`.
  - genusTypeId. A string field useful for UIs in differentiating between `item` types. This is
                 pre-determined for you and should not be arbitrarily modified.
  - aliasId. A non-qbank ID that you would to reference the `item` by. For example, when
             transferring items from Onyx, we can set an `aliasId` with the Onyx ID, and then
             be able to retrieve the `item` using that ID instead of the qbank generated one.
  - question. A dictionary that includes a set of values defining the question.
    - questionString. The text prompt of the question. Example: Who crashed into Kanasu?
    - choices. For multiple choice, reflection, moveable words, and image sequence.
               This is a list of objects, with each choice specifying an optional `id` and
               its `text`. The `id` can be useful if porting from another system, like Onyx.
    - inlineRegions. For fill-in-the-blank, this is a set of key:value pairs, where the `key`
                     represents the region ID for the blank. `value` is then an object
                     with `choices` as a list of `id` and `text` objects, as above.
  - answers. 

form data (multi-language, shared across all `item` types, optional):
  - name. A new language name / title for the `item`.
  - description. A new language description for the `item`.
  - editName. To replace the name in a specific language, you can include either just the text
              and declare the `x-api-locale` header, or you can provide the entire
              `DisplayText` object.
  - removeName. To specify an existing language value to remove. Note that this looks for
                a string + language setting match, not just the language setting match.
  - editDescription. To replace the description in a specific language, you can include either
                     just the text and declare the `x-api-locale` header, or you can provide
                     the entire `DisplayText` object.
  - removeDescription. To specify an existing language value to remove. Note that this looks for
                       a string + language setting match, not just the language setting match.
  - genusTypeId. A string field useful for UIs in differentiating between `item` types. This is
                 pre-determined for you and should not be arbitrarily modified.
  - aliasId. A non-qbank ID that you would to reference the `item` by. For example, when
             transferring items from Onyx, we can set an `aliasId` with the Onyx ID, and then
             be able to retrieve the `item` using that ID instead of the qbank generated one.
  - question. A dictionary that includes a set of values defining the question.
    - questionString. A new text prompt, in the specified language (`x-api-locale` or as
                      `DisplayText`). Example: Who crashed into Kanasu?
    - oldQuestionString and newQuestionString. To replace a specific language string with a new one.
                                               Must both be present. Can be specified with either
                                               `x-api-locale` or `DisplayText`)
    - removeQuestionString. A question string in a specified language, to remove. Note that this
                            expects a string + language settings match. Can be specified either
                            with `x-api-locale` or `DisplayText`.
    - choices. For multiple choice, reflection, moveable words, and image sequence.
               This is a list of objects. If `id`, `oldText`, and `newText` are provided,
               then the corresponding text value for the given language is replaced.
               If `id` and `removeText` are provided, then the matching text + language value
               is removed. Otherwise, a new text object is added / created with the choice `text`
                value (with the optional `id` parameter either defined by the user or
                generated by qbank).
    - inlineRegions. For fill-in-the-blank, this is a set of key:value pairs, where the `key`
                     represents the region ID for the blank. `value` is then an object
                     with `choices` as a list of objects, as defined above.


