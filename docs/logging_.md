# Logging Service

## Headers

QBank uses various headers to represent the user and settings. They are outlined below.

`x-api-proxy`: The username or a sessionId (from unplatform). `LogEntries` will all be tagged
               with this sessionId, so it is important that this matches the
               unplatform data.

## URLs

The following are in the schema of `url` -> `sub-heading`

```
/logs -> LogsList
/logs/(.*)/logentries/(.*) -> LogEntryDetails
/logs/(.*)/logentries -> LogEntriesList
/logs/(.*) -> LogDetails
```

### LogsList

List all available `log`s.
`/api/v2/logging/logs`

#### GET

url parameters (optional):
  - None currently supported

returns:
  - list of `Log` objects.

#### POST

To create a new `log`, you can either supply a `name` and `description`,
or alternatively supply an assessment `bank` ID. If you supply a `bankId`,
then the log will be orchestrated to have a matching internal identifier.
i.e. `assessment.Bank%3A111111111111111111111111%40ODL.MIT.EDU` would
generate a `log` with ID `logging.Log%3A111111111111111111111111%40ODL.MIT.EDU`.
In this case, the `name` and `description` can be left out (default ones
will be provided), but you can also supply your own.

form data (optional):
  - name. A name / title for the `log` that will help authors identify it in a UI. Limited
          to 256 characters. Will be set to the default language of `en`.
  - description. A longer text field to describe the `log`. Limited to 1024 characters.
                 Will be set to the default language of `en`.
  - genusTypeId. A string field useful for UIs in differentiating between `log` types. Only
                 used in CLIx to identify a "default" log that unplatform uses
                 when no `log` ID is available.
  - bankId. A source assessment `bank` ID, if orchestration is desired.

returns:
  - `Log` object.

### LogEntryDetails

Get, edit, or delete a log entry
`/api/v2/logging/logs/<log_id>/logentries/<entry_id>`

#### DELETE

returns:
  - 202.

#### GET

url parameters (optional):
  - None currently supported

returns:
  - `LogEntry` object.

#### PUT

headers (expected):
  - x-api-proxy. This will be included with the `log entry` as the "agent" that created the
                 entry.

form data (optional):
  - data. A text blob or object (that will get stringified), which is inserted
          as the "text" value of the `log entry`.

returns:
  - the updated `LogEntry` object.

### LogEntriesList

Get or add `log entry` to a specific `log`
`/api/v2/logging/logs/<log_id>/logentries`

#### GET

url parameters (optional):
  - None currently supported

returns:
  - list of `LogEntry` objects.

#### POST

headers (expected):
  - x-api-proxy. This will be included with the `log entry` as the "agent" that created the
                 entry.

form data (optional):
  - data. A text blob or object (that will get stringified), which is inserted
          as the "text" value of the `log entry`.

returns:
  - the updated `LogEntry` object.

### LogDetails

Get, edit, or delete a specific `log`.
`/api/v2/logging/logs/<log_id>`

#### DELETE

returns:
  - 202.

#### GET

url parameters (optional):
  - None currently supported

returns:
  - `Log` object.

#### PUT

form data (optional):
  - name. A name / title for the `log` that will help authors identify it in a UI. Limited
          to 256 characters. Will be set to the default language of `en`.
  - description. A longer text field to describe the `log`. Limited to 1024 characters.
                 Will be set to the default language of `en`.

