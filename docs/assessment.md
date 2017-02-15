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
/banks/(.*)/assessments/(.*)/assignedbankids/(.*) -> AssessmentRemoveAssignedBankIds
/banks/(.*)/assessments/(.*)/assignedbankids -> AssessmentAssignedBankIds
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
  - `AssessmentTaken` object.

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
  - `AssessmentOffered` object.

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
  - genusTypeId. This can be used to define the "type" of `offered`, i.e. to display all questions on a
                 single page or one at a time. Client-defined. This should be of the form:
                 `assessment-offered-genus-type%3A<some identifier>%40ODL.MIT.EDU`, like
                 `assessment-offered-genus-type%3Asingle-page%40ODL.MIT.EDU`

returns:
  - the updated `AssessmentOffered` object.

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
  - question object with `responded` key. If `responded` is `True`, will also return a `correct` key
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
  - list of question objects. Does not include `responded` or `correct` status.

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
  - `AssessmentTaken` object.

### AssessmentsOffered

Get or create `offered`s of an `assessment`
`/api/v1/assessment/banks/<bank_id>/assessments/<assessment_id>/assessmentsoffered`

#### GET

url parameters (optional):
  - None currently supported

returns:
  - list of `AssessmentOffered` objects.

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
  - genusTypeId. This can be used to define the "type" of `offered`, i.e. to display all questions on a
                 single page or one at a time. Client-defined. This should be of the form:
                 `assessment-offered-genus-type%3A<some identifier>%40ODL.MIT.EDU`, like
                 `assessment-offered-genus-type%3Asingle-page%40ODL.MIT.EDU`

### AssessmentRemoveAssignedBankIds

Remove a current value from the `assignedBankIds` list for an `assessment`.

Note that an `assessment` must always belong to at least **one** `bank`, so an exception will
be thrown if you attempt to remove them all.

`/api/v1/assessment/banks/<bank_id>/assessments/<assessment_id>/assignedbankids/<assigned_bank_id>`

#### DELETE

Remove a single `bankId`.

returns:
  - 202.

### AssessmentAssignedBankIds

Add an `assignedBankIds` to an `assessment`. Used in CLIx for publishing / unpublishing
an assessment.

`/api/v1/assessment/banks/<bank_id>/assessments/<assessment_id>/assignedbankids`

#### POST

Add the provided `bankId`s to the `assessment`. This does **not** remove the current
 `assignedBankIds`, only appends.

form data (required):
  - assignedBankIds: list of new `bankId`s. Can be aliased or not.
                     Example: ["assessment.Bank%3A5877df4e71e482663913eefc%40ODL.MIT.EDU"]

returns:
  - 202.


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
  - list of `Item` objects.

#### POST

This is a full-replace endpoint, and will replace the current list of `item`s in the assessment.
This can also be used to re-order `item`s.

form data (required):
  - itemIds. List of `item` IDs, in the desired final order.

returns:
  - list of `item` objects.

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
  - `Assessment` object.

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
  - itemIds. A list of `item` IDs to appear in the `assessment`.

returns:
  - `Assessment` object. Note that this does **not** include the `item`s.

### AssessmentsList

Get a list of all `assessment`s in the specified `bank`. Also create an `assessment`.
`/api/v1/assessment/banks/<bank_id>/assessments`

#### GET

url parameters (optional):
  - isolated. Will only return the `assessments` from the provided `bankId`. Will **not**
              traverse the hierarchy down.

returns:
  - list of `Assessment` objects.

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
  - assignedBankIds. In addition to the URL parameter, you can pass in a list of `bankId`s
                     to assign the new `assessment` to. These can be aliased or not.
  - itemIds. A list of valid `itemId` strings to assign to the assessment. The assumption is
             that these already exist in the system.

returns:
  - `Assessment` object. Note that this does **not** include the `item`s.

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
  - `Item` object.

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
  - `Item` object. For convenience, wrong answers are also included in the response.

#### PUT

Note that the form data will differ for multi-language `item`s. Older `item`s will not
have this kind of support. You can identify if an `item` (or question, answer) is multi-language
by looking at its `recordTypeIds` property. If it has values like
`osid-object%3Amulti-language%40ODL.MIT.EDU`, then you need to use the multi-language form
values specified below.

Also, as with submitting responses to questions, the form data for each type of `item` differs.

form data (single language, optional):
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
                      Note that for QTI questions, this is expected to be wrapped in an `<itemBody>`
                      object with the appropriate HTML markup (`p`, `div`, etc. as necessary).
    - choices. For multiple choice, reflection, moveable words, and image sequence.
               This is a list of objects, with each choice specifying an optional `id` and
               its `text`. The `id` can be useful if porting from another system, like Onyx.
               Note that for QTI questions, this is expected to be wrapped in the
               appropriate choice object, like `<simpleChoice>`.
    - inlineRegions. For fill-in-the-blank, this is a set of key:value pairs, where the `key`
                     represents the region ID for the blank. `value` is then an object
                     with `choices` as a list of `id` and `text` objects, as above.
    - variables. A list of variable objects used in parameterized numeric response questions.
                 Each object must have `id`, `type` (`int` or `float`), `min`, `max`, and optional
                 `step` and `format` (for `float`) values. The `id` value must match what
                 is present in the `questionString`.
  - answers. A list of answer objects (correct or incorrect). Correctness is indicated in the
             `genusTypeId` property, and the exact format of the answer object depends
             on the type of question. With this endpoint, you can add, remove, or edit
             answers. Feedback is attached to specific answers. If a feedback requires
             a new file `asset`, like an image or audio clip, this endpoint assumes that
             the `asset` already exists and you can provide the `assetId`.
    - id. If editing an existing answer, provide the qbank ID of the answer. Otherwise
          this endpoint will create a new answer.
    - delete. If passed as `true`, this will delete the given `answer`.
    - genusTypeId. Correct answers should have this set to `answer-type%3Aright-answer%40ODL.MIT.EDU`.
                   Incorrect answers should have this set to `answer-type%3Awrong-answer%40ODL.MIT.EDU`.
    - fileIds. If necessary, this is a list of objects, indicating new `asset`s attached
               to this answer. Each object must include `assetId`, `assetContentId`, and
               `assetContentTypeId`.
    - feedback. A text feedback to be provided to the student, on submit of the given answer.
    - confusedLearningObjectiveIds. A list of string IDs, representing learning outcomes associated
                                    with the corresponding answer (right or wrong).
    - type. Valid values are:
        `answer-record-type%3Amulti-choice-answer%40ODL.MIT.EDU` for multiple choice, reflection,
            moveable words, image sequence.
        `answer-record-type%3Ainline-choice-answer%40ODL.MIT.EDU` for fill-in-the-blank.
        `answer-record-type%3Afiles-submission%40ODL.MIT.EDU` for any moveable word sandbox, audio
            record tool, and generic file submission.
        `answer-record-type%3Ashort-text-answer%40ODL.MIT.EDU` for short answer text response.
    - choiceIds (for multiple choice-type questions). A list of choice IDs. For most types of
        questions, this is evaluated without regard to order. For image sequence and moveable
        words sentence, order matters.
    - region (for fill-in-the-blank). Must also be used in conjunction with `choiceIds`. Specifies
        the specific "blank" that the choices are being submitted for.

form data (multi-language, optional):
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
                      Note that for QTI questions, this is expected to be wrapped in an `<itemBody>`
                      object with the appropriate HTML markup (`p`, `div`, etc. as necessary).
    - oldQuestionString and newQuestionString. To replace a specific language string with a new one.
                                               Must both be present. Can be specified with either
                                               `x-api-locale` or `DisplayText`).
                                               Note that for QTI questions, this is expected to be
                                               wrapped in an `<itemBody>`
                                               object with the appropriate HTML markup
                                               (`p`, `div`, etc. as necessary).
    - removeQuestionString. A question string in a specified language, to remove. Note that this
                            expects a string + language settings match. Can be specified either
                            with `x-api-locale` or `DisplayText`.
    - choices. For multiple choice, reflection, moveable words, and image sequence.
               This is a list of objects. If `id`, `oldText`, and `newText` are provided,
               then the corresponding text value for the given language is replaced.
               If `id` and `removeText` are provided, then the matching text + language value
               is removed. Otherwise, a new text object is added / created with the choice `text`
               value (with the optional `id` parameter either defined by the user or
               generated by qbank). Note that for QTI questions, this is expected to be wrapped in the
               appropriate choice object, like `<simpleChoice>`.
    - inlineRegions. For fill-in-the-blank, this is a set of key:value pairs, where the `key`
                     represents the region ID for the blank. `value` is then an object
                     with `choices` as a list of objects, as defined above.
    - variables. A list of variable objects used in parameterized numeric response questions.
                 Each object must have `id`, `type` (`int` or `float`), `min`, `max`, and optional
                 `step` and `format` (for `float`) values. The `id` value must match what
                 is present in the `questionString`.
    - timeValue. A dictionary with (optional) keys `hours`, `minutes`, `seconds`, to set a
                 time value on the question, for example a limit of audio recording time.
  - answers. A list of answer objects (correct or incorrect). Correctness is indicated in the
             `genusTypeId` property, and the exact format of the answer object depends
             on the type of question. With this endpoint, you can add, remove, or edit
             answers. Feedback is attached to specific answers. If a feedback requires
             a new file `asset`, like an image or audio clip, this endpoint assumes that
             the `asset` already exists and you can provide the `assetId`.
    - id. If editing an existing answer, provide the qbank ID of the answer. Otherwise
          this endpoint will create a new answer.
    - delete. If passed as `true`, this will delete the given `answer`.
    - genusTypeId. Correct answers should have this set to `answer-type%3Aright-answer%40ODL.MIT.EDU`.
                   Incorrect answers should have this set to `answer-type%3Awrong-answer%40ODL.MIT.EDU`.
    - fileIds. If necessary, this is a list of objects, indicating new `asset`s attached
               to this answer. Each object must include `assetId`, `assetContentId`, and
               `assetContentTypeId`.
    - feedback. A text feedback to be provided to the student, on submit of the given answer.
                This is set to the language defined in `x-api-locale` or as the `DisplayText` object.
    - oldFeedback and newFeedback. Must be used together. This is used to replace a specific string +
                                   language setting match for the feedback field.
    - removeFeedback. This removes a single string + language setting match for the feedback field.
    - confusedLearningObjectiveIds. A list of string IDs, representing learning outcomes associated
                                    with the corresponding answer (right or wrong).
    - type. Valid values are:
        `answer-record-type%3Amulti-choice-answer%40ODL.MIT.EDU` for multiple choice, reflection,
            moveable words, image sequence.
        `answer-record-type%3Ainline-choice-answer%40ODL.MIT.EDU` for fill-in-the-blank.
        `answer-record-type%3Afiles-submission%40ODL.MIT.EDU` for any moveable word sandbox, audio
            record tool, and generic file submission.
        `answer-record-type%3Ashort-text-answer%40ODL.MIT.EDU` for short answer text response.
    - choiceIds (for multiple choice-type questions). A list of choice IDs. For most types of
        questions, this is evaluated without regard to order. For image sequence and moveable
        words sentence, order matters.
    - region (for fill-in-the-blank). Must also be used in conjunction with `choiceIds`. Specifies
        the specific "blank" that the choices are being submitted for.

returns:
  - the updated `Item` object. For convenience, wrong answers are also included in the response.

### ItemsList

Return list of `item`s in the given assessment `bank`.
`/api/v1/assessment/banks/<bank_id>/items`

#### GET

url parameters (optional):
  - displayName. Query / filter by the given text in the displayName field.
                 Case insensitive matching.
  - displayNames. Query / filter by the given text in the displayName field.
                  Case insensitive matching. Works across all language fields.
  - genusTypeId. Query / filter by the genusTypeId of an `item`.
  - qti. Include the QTI 1 XML in the response objects.
  - isolated. Only check the current `bankId` for `item`s. Do **not** check child `bank`s.

returns:
  - list of `Item` objects. Note that wrong answers are **not** included.

#### POST

You can either submit a valid, supported QTI *.zip file, or create items via REST.

Note that when creating `item`s via REST, you **must** first upload all associated
files, via the `repository` endpoint for `asset`s. This is demonstrated in
`tests/test_assessment.py` in the class `QTIEndpointTests` method called `upload_media_file`.

Full RESTful documentation is probably best done by example, in viewing the tests.
You can see the RESTful tests in `tests.test_assessment.py`, specifically the
`QTIEndpointTests` class. Note that it is preferred, when creating items via REST,
to upload text without the QTI-specific wrappers like `<itemBody>` and `<simpleChoice>`.
That way the questions can easily be reformatted to other standards.
You can also refer to `ItemDetails` `PUT` above for more details.

Useful tests to reference are:
  - test_item_body_and_inline_choice_tags_provided_inline_choice
  - test_item_body_and_simple_choice_tags_provided_multiple_choice
  - test_item_body_and_simple_choice_tags_provided_order_interaction
  - test_item_body_provided_audio_upload
  - test_item_body_provided_numeric_response
  - test_can_create_audio_record_tool_question_via_rest
  - test_can_create_fill_in_the_blank_question_via_rest
  - test_can_create_generic_file_upload_question_via_rest
  - test_can_create_image_sequence_question_via_rest
  - test_can_create_multi_choice_multi_answer_question_via_rest
  - test_can_create_multi_choice_single_answer_question_via_rest
  - test_can_create_mw_sandbox_question_via_rest
  - test_can_create_mw_sentence_question_via_rest
  - test_can_create_numeric_response_question_via_rest
  - test_can_create_reflection_multi_answer_question_via_rest
  - test_can_create_reflection_single_answer_question_via_rest
  - test_can_create_short_answer_question_via_rest

Supported `item` `genusTypeId`s are:
  - item-genus-type%3Aqti-choice-interaction%40ODL.MIT.EDU
  - item-genus-type%3Aqti-choice-interaction-multi-select%40ODL.MIT.EDU
  - item-genus-type%3Aqti-choice-interaction-survey%40ODL.MIT.EDU
  - item-genus-type%3Aqti-choice-interaction-multi-select-survey%40ODL.MIT.EDU
  - item-genus-type%3Aqti-upload-interaction-audio%40ODL.MIT.EDU
  - item-genus-type%3Aqti-upload-interaction-generic%40ODL.MIT.EDU
  - item-genus-type%3Aqti-order-interaction-mw-sentence%40ODL.MIT.EDU
  - item-genus-type%3Aqti-order-interaction-mw-sandbox%40ODL.MIT.EDU
  - item-genus-type%3Aqti-order-interaction-object-manipulation%40ODL.MIT.EDU
  - item-genus-type%3Aqti-extended-text-interaction%40ODL.MIT.EDU
  - item-genus-type%3Aqti-inline-choice-interaction-mw-fill-in-the-blank%40ODL.MIT.EDU
  - item-genus-type%3Aqti-numeric-response%40ODL.MIT.EDU

Supported `question` `genusTypeId`s are:
  - question-type%3Aqti-choice-interaction%40ODL.MIT.EDU
  - question-type%3Aqti-choice-interaction-multi-select%40ODL.MIT.EDU
  - question-type%3Aqti-choice-interaction-survey%40ODL.MIT.EDU
  - question-type%3Aqti-choice-interaction-multi-select-survey%40ODL.MIT.EDU
  - question-type%3Aqti-upload-interaction-audio%40ODL.MIT.EDU
  - question-type%3Aqti-upload-interaction-generic%40ODL.MIT.EDU
  - question-type%3Aqti-order-interaction-mw-sentence%40ODL.MIT.EDU
  - question-type%3Aqti-order-interaction-mw-sandbox%40ODL.MIT.EDU
  - question-type%3Aqti-order-interaction-object-manipulation%40ODL.MIT.EDU
  - question-type%3Aqti-extended-text-interaction%40ODL.MIT.EDU
  - question-type%3Aqti-inline-choice-interaction-mw-fill-in-the-blank%40ODL.MIT.EDU
  - question-type%3Aqti-numeric-response%40ODL.MIT.EDU

Supported `answer` `genusTypeId`s are:
  - answer-type%3Aright-answer%40ODL.MIT.EDU
  - answer-type%3Awrong-answer%40ODL.MIT.EDU


form data (one of the following is required):
  - qtiFile. QTI 1 zip file.
  - JSON blob with valid data.

### AssessmentBankDetails

Shows details for, edit, or delete a specific assessment `bank`.
`/api/v1/assessment/banks/<bank_id>`

#### DELETE

returns:
  - 202.

#### GET

url parameters (optional):
  - None currently supported

returns:
  - `Bank` object.

#### PUT

form data (optional):
  - name. A name / title for the `bank` that will help authors identify it in a UI. Limited
          to 256 characters. Will be set to the default language of `en`.
  - description. A longer text field to describe the `bank`. Limited to 1024 characters.
                 Will be set to the default language of `en`.
  - genusTypeId. A string field useful for UIs in differentiating between `bank` types. This is
                 pre-determined for you and should not be arbitrarily modified.

returns:
  - the updated `Bank` object.

### AssessmentBanksList

List all available assessment `bank`s.
`/api/v1/assessment/banks`

#### GET

url parameters (optional):
  - displayName. Query / filter by the given text in the displayName field.
                 Case insensitive matching.
  - genusTypeId. Query / filter by the genusTypeId of a `bank`.

returns:
  - list of `Bank` objects.

#### POST

form data (optional):
  - name. A name / title for the `bank` that will help authors identify it in a UI. Limited
          to 256 characters. Will be set to the default language of `en`.
  - description. A longer text field to describe the `bank`. Limited to 1024 characters.
                 Will be set to the default language of `en`.
  - genusTypeId. A string field useful for UIs in differentiating between `bank` types. This can
                 be set to any string value that matches the format
                 `<namespace>%3A<identifier>%40<authority>`. For example, we use it in CLIx to
                 differentiate between subjects and units.
                 `bank-genus-type%3Aclix-grade%40ODL.MIT.EDU`
                 `bank-genus-type%3Aclix-domain%40ODL.MIT.EDU`
                 `bank-genus-type%3Aclix-subdomain%40ODL.MIT.EDU`
                 `bank-genus-type%3Aclix-unit%40ODL.MIT.EDU`
                 `bank-genus-type%3Aclix-lesson%40ODL.MIT.EDU`
                 `bank-genus-type%3Aclix-activity%40ODL.MIT.EDU`
                 `bank-genus-type%3Aclix-archive%40ODL.MIT.EDU

returns:
  - the new `Bank` object.

### AssessmentHierarchiesRootDetails

List the bank details for a root `bank`. Allow you to remove it as a root.
`/api/v1/assessment/hierarchies/roots/<bank_id>`

#### DELETE

Note that this only removes the `bank` as a root `bank` -- the `bank` is **not** deleted
from the system.

returns:
  - 202.

#### GET

url parameters (optional):
  - None currently supported

returns:
  - `BankNode` object. Note that the ID corresponds to the `bank` ID, though the object
    is slightly different.

### AssessmentHierarchiesRootsList

List all available assessment hierarchy root `node`s. Note that the nodes must exist as
`bank`s prior to being added as a root `node`.
`/api/v1/assessment/hierarchies/roots`

#### GET

url parameters (optional):
  - None currently supported

returns:
  - list of `BankNode` objects. Note that the IDs correspond to the `bank` IDs, though the
    objects are slightly different.

#### POST

This adds an existing assessment `bank` as a root `node` in the hierarchy system.

form data (required):
  - id. The `bankId` of the assessment `bank` you want to add as a root.

returns:
  - 201.

### AssessmentHierarchiesNodeChildrenList

List the children for a root `node`.
`/api/v1/assessment/hierarchies/nodes/<bank_id>/children`

#### GET

By default, this returns descendants only 1 level deep.

url parameters (optional):
  - descendants. The level of depth in the hierarchy tree that you want returned. CLIx data
                 is about 6 levels deep.
  - display_names. For convenience, if you want the `bank`'s displayName field appended to
                   the `node`, so you don't need to retrieve it separately when showing the
                   hierarchy.

returns:
  - list of `BankNode` objects. Note that the IDs correspond to the `bank` IDs, though the
    objects are slightly different. Children nodes are included in the `childNodes` attribute,
    as a list of `BankNode` objects.

#### POST

Note that this does a full replacement of the children `node`s, so there may be concurrency
issues.

form data (required):
  - ids. List of `bank` IDs. Note that returned order is not guaranteed.

returns:
  - 201.

### AssessmentHierarchiesNodeDetails

List the `bank` details for a `node`.
`/api/v1/assessment/hierarchies/nodes/<bank_id>`

#### GET

By default, this returns no descendants or ancestors.

url parameters (optional):
  - descendants. The level of depth in the hierarchy tree that you want returned. CLIx data
                 is about 6 levels deep.
  - ancestors. The level of depth "up" the hierarchy tree that you want returned. CLIx data
               is about 6 levels deep.

returns:
  - `BankNode` object. Note that the ID corresponds to the `bank` ID, though the
    object is slightly different. Children nodes are included in the `childNodes` attribute,
    as a list of `BankNode` objects. Ancestor nodes are included in the `parentNodes`
    attribute.
