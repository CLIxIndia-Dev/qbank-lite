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

You can use this endpoint to update four things in an `assetContent`.
Multi-language `assetContent`s support multiple text fields.
  - the actual data / bits.
  - the `displayName`.
  - the `description`.
  - the `genusTypeId`.

form data (optional):
  - inputFile. The new file data that you want the `asset content` to
               contain. The ID is not changed.
  - genusTypeId. The `genusTypeId` of the `asset content`, like:
                 `asset-content-genus-type%3Athumbnail%40ODL.MIT.EDU` for a thumbnail image.
  - displayName. Can be a `displayText` object or a string (in which case the
                 language and script fields are set from the `x-api-locale` header).
  - editName. A two-item list of the name text you want replaced (with language info).
              Should be `[<old string>, <new string>]`.
  - removeName. The text object / string you want removed from the `displayNames`.
  - description. Can be a `displayText` object or a string (in which case the
                 language and script fields are set from the `x-api-locale` header).
  - editDescription. A two-item list of the description text you want replaced (with language info).
                     Should be `[<old string>, <new string>]`.
  - removeDescription. The text object / string you want removed from the `descriptions`.

returns:
  - the `asset` that the content belongs to.

### AssetDetails

Get `asset` details.

Note that if you provide the `x-api-locale` header, any `assetContents`
that have multi-language `displayName` or `description` will be returned
in the given `locale`.

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