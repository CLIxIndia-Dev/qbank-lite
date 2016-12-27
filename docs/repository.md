# Repository Service

## Headers

QBank uses various headers to represent the user and settings. They are outlined below.

`x-api-proxy`: The username or a sessionId (from unplatform).

## URLs

The following are in the schema of `url` -> `sub-heading`

```
/repositories/(.*)/assets/(.*)/contents/(.*) -> AssetContentDetails
/repositories/(.*)/assets/(.*) -> AssetDetails
/repositories/(.*)/assets -> AssetsList
/repositories/(.*) -> RepositoryDetails
/repositories -> RepositoriesList
```

### AssetContentDetails

Serves up the specified `asset content` file, so images, audio clips,
and videos appear correctly in the browser.
`/api/v2/repository/repositories/<repository_id>/assets/<asset_id>/contents/<content_id>`

#### GET

url parameters (optional):
  - None currently supported

returns:
  - file contents of the specified `asset content`.

#### PUT

You would use this to replace the data for a single `asset content`.
It has been used by some CLIx scripts when you want to keep the same `fileId` and
pointer in `item`s...it is **not** recommended to use this endpoint for
actual content management. The ideal tool would create a new `asset` with
new `asset content` instead of replacing just the data.

This is included for reference only.

form data (required):
  - inputFile. The new file data that you want the `asset content` to
               contain. The ID is not changed.

returns:
  - the `asset` that the content belongs to.

### AssetDetails

Get `asset` details for the given `repository`
`/api/v2/repository/repositories/<repository_id>/assets/<asset_id>`

#### GET

url parameters (optional):
  - None currently supported

returns:
  - `Asset` object.

### AssetsList

Return list of `asset`s in the given `repository`, or create a new
`asset`.
`/api/v2/repository/repositories/<repository_id>/assets`

#### GET

url parameters (optional):
  - None currently supported

returns:
  - list of `Asset` objects.

#### POST

form data (required):
  - inputFile. The file that you want to save into an `asset content`.
               This version of the RESTful API abstracts out the idea
               of separate `asset` and `asset content` and instead treats
               them as the same object.

returns:
  - `Asset` object.

### RepositoryDetails

Shows details for a specific `repository`. This can be orchestrated with an
existing assessment `bank` if you pass in a `bank_id`. Currently, this is
the only way you would create a `repository` for CLIx.
`/api/v2/repository/repositories/<repository_id>`

#### GET

url parameters (optional):
  - None currently supported

returns:
  - `Repository` object.

### RepositoriesList

List all available `repositories`.
`/api/v2/repository/repositories`

#### GET

url parameters (optional):
  - None currently supported

returns:
  - list of `Repository` objects.