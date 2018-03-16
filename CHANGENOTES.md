## [3.16.4] - 2018-03-16:
### Changed
  - Upgraded `dlkit` to `0.6.8` to fix `django` config.

## [3.16.3] - 2018-03-16:
### Added
  - `AssessmentTaken` RESTful functionality improved to support
    some features needed for the StarLogoNova integration.

## [3.16.2] - 2018-03-08:
### Changed
  - Updated `dlkit` to `0.6.4` to fix some bugs related to catalog
    orchestration and django.

## [3.16.1] - 2018-03-01:
### Changed
  - Updated `dlkit` to `0.6.2` to improve performance of FilesRecord
    when retrieving AssetContent URLs.

## [3.16.0] - 2018-02-28:
### Changed
  - Updated `dlkit` to `0.6.0` to add `diskcache` option and config.
    This changes the default caching engine to `diskcache` instead
    of `memcache`. To continue using `memcache`, use the `cachingEngine`
    config for `dlkit`.

## [3.15.11] - 2018-02-23:
### Changed
  - Updated `dlkit` to `0.5.18` for minor bugs.

### Fixed
  - Enforce response form record types, to match item genus.

## [3.15.10] - 2018-01-17:
### Changed
  - Updated `dlkit` to `0.5.17` for `memcached` config.

## [3.15.9] - 2017-12-08:
### Changed
  - Set `os.chdir()` to find files in application bundle.
  - Detect platform for recursion limit in `main.spec`.

## [3.15.8] - 2017-12-05:
### Changed
  - Cleaned up old requirements.

## [3.15.7] - 2017-12-05:
### Added
  - Hidden import for accessibility records, in main.spec.

## [3.15.6] - 2017-09-13:
### Changed
  - Update `dlkit` to `0.5.13` and update tests.

## [3.15.5] - 2017-07-11:
### Changed
  - Update `dlkit` to `0.5.3` for `cataloging` package.

## [3.15.4] - 2017-06-13:
### Changed
  - Update `dlkit` to `0.5.2` for `pymongo` 2 compatibility.

## [3.15.3] - 2017-06-07:
### Fixed
  - Allow you to upload the first asset metadata file on PUT,
    even if you didn't include it in the original POST.

## [3.15.2] - 2017-06-06:
### Fixed
  - Off-by-one when returning byte range for streaming asset contents.

## [3.15.1] - 2017-06-06:
### Fixed
  - Typo in adding record to assessment offered.

### Changed
  - Updated `dlkit` to `0.5.1` to keep `unlockPrevious` as
    a simple string.

## [3.15.0] - 2017-06-05:
### Added
  - Update `dlkit` to `0.5.0` to add `UnlockPrevious` record.
  - RESTful support for `UnlockPrevious` record.

## [3.14.10] - 2017-05-31:
### Changed
  - Update `dlkit` to `0.4.2` for Python 2 / 3 compatibility.

## [3.14.9] - 2017-05-11:
### Fixed
  - Update `dlkit` to fix bug with `None` text.
  - Account for `None` feedback text.
  - Enforce typing for `add_asset()` method.

## [3.14.8] - 2017-05-08:
### Changed
  - Update `spec` file with hidden `dlkit` imports
    for `pyinstaller`.
  - Update `pyinstaller` to `3.2.1`.

## [3.14.7] - 2017-05-08:
### Changed
  - Update `dlkit` from `0.3.3` to `0.3.6`.

## [3.14.6] - 2017-05-03:
### Fixed
  - Fixed traceback on development, for `IllegalState`.

## [3.14.5] - 2017-05-03:
### Fixed
  - Changing choice order ignores duplicate `choiceId`s.

## [3.14.4] - 2017-04-28:
### Removed
  - `webapps` directory from the repo.

## [3.14.3] - 2017-04-26:
### Changed
  - Switched to using `dlkit` installable package from
    `pip`, instead of git submodules.

## [3.14.2] - 2017-04-20:
### Changed
  - `isCorrect: None` appears in offered results for
    every question, by default, when they have not
    been responded to.

## [3.14.1] - 2017-04-19:
### Fixed
  - Also check WSGI environment variables for development.

## [3.14.0] - 2017-04-19:
### Changed
  - Provide exception tracebacks on dev environments.

## [3.13.1] - 2017-04-18:
### Fixed
  - Test fixtures updated for MongoDB and filesystem.

## [3.13.0] - 2017-04-18:
### Added
  - `provider` field for `asset` forms. Maps to citation.

## [3.12.0] - 2017-04-18:
### Added
  - `source` field for `asset` forms.

## [3.11.6] - 2017-04-14:
### Changed
  - Render the transcript as sibling to the parent `<p>`
    tag so there is valid HTML on the UI-side.

## [3.11.5] - 2017-04-13:
### Fixed
  - JSONify `altText` and `mediaDescription` on `PUT`, too.

## [3.11.4] - 2017-04-13:
### Fixed
  - JSONify `altText` and `mediaDescription` when they
    are sent as JSON strings in forms.

## [3.11.3] - 2017-04-12:
### Changed
  - Updated dlkit to include cataloging support.

## [3.11.2] - 2017-04-11:
### Changed
  - For VTT asset contents, return the wrapper url instead of
    a language-specific url, when embedding the VTT file inside
    of an item.

## [3.11.1] - 2017-04-10:
### Fixed
  - Account for response map when inherits from feedback record.

## [3.11.0] - 2017-04-10:
### Added
  - `additionalAttempts` flag to get all user responses in
    offered results.

## [3.10.0] - 2017-04-07:
### Added
  - Support the `/stream` endpoint for transcript and VTT text.

## [3.9.2] - 2017-04-07:
### Fixed
  - Apply float formatting to numeric response to prevent
    sympy precision resulting in "incorrect" evaluations.

## [3.9.1] - 2017-04-07:
### Fixed
  - Changed `get_asset_id()` method name to prevent overriding.

## [3.9.0] - 2017-04-07:
### Added
  - Question string support for drag-and-drop.

## [3.8.6] - 2017-04-07:
### Fixed
  - Honor format for float numeric response questions.

## [3.8.5] - 2017-04-07:
### Changed
  - Only save asset content files once; do filename replacement
    in the `filesystem_adapter`.

## [3.8.4] - 2017-04-07:
### Fixed
  - Account for drag-and-drop questions when getting taken
    questions with `?qti` flag.

## [3.8.3] - 2017-04-07:
### Fixed
  - Reverted 3.7.7 to test server IOError fix.

## [3.8.2] - 2017-04-04:
### Fixed
  - Change the `create_test_repository` import.

## [3.8.1] - 2017-04-04:
### Fixed
  - Make the test for `allAssets` more robust.

## [3.8.0] - 2017-04-03:
### Added
  - `allAssets` flag to get all `assets` in the system.

## [3.7.7] - 2017-04-03:
### Added
  - Close the file pointer after streaming the asset content.

## [3.7.6] - 2017-03-31:
### Fixed
  - Updated test config to use filesystem.
  - Updated dlkit to fix bugs when deleting asset contents when using
    filesystem.

## [3.7.5] - 2017-03-30:
### Fixed
  - Changed the `mediaDescription` `genusTypeId` to `media-description`
    for consistency.

## [3.7.4] - 2017-03-30:
### Fixed
  - Update the records submodule URL.

## [3.7.3] - 2017-03-30:
### Fixed
  - Make single-language feedbacks also return a DisplayText.

## [3.7.2] - 2017-03-30:
### Added
  - New tests for image sequence submissions.

## [3.7.1] - 2017-03-30:
### Fixed
  - Fix for always-correct question types.

## [3.7.0] - 2017-03-29:
### Added
  - Convenience methods for adding VTT and transcript files.
  - VTT and transcript files appear in items when the `src` tags
    are applied correctly.

3.6.0:
  - Convenience methods for adding media alt-text and descriptions.

3.5.2:
  - Refactor item response validation.

3.5.1:
  - Account for drag and drop targets / zones / droppables with no `name`
    value provided on create.

3.5.0:
  - Simple refactors to try and improve getQuestions and Submit performance.

3.4.1:
  - Fix `app_configs/configs.py` to use filespace, to work for field
    deployments.

3.4.0:
  - Clean up dlkit submodule URLs.

3.3.0:
  - Support drag-and-drop problem types.

3.2.1:
  - Do not escape feedback when provided without `<modalFeedback>` tag.

3.2.0:
  - Update main.spec to dynamically calculate the pathex argument.

3.1.1:
  - Remove old reference to dlkit-lite in .gitmodules.

3.1.0:
  - Can replace an existing variable value for numeric response questions.

3.0.1:
  - Change DLKit `json` to `json_` to avoid collisions.

3.0.0:
  - Switch to DLKit generic JSON impl; requires changes in app_configs/configs.py
    and app_configs/registry.py.

2.1.6:
  - Added in missing `TEST_ABS_PATH` declaration for bundled scenario, in configs.

2.1.5:
  - Added better 206 header management for streaming content.

2.1.4:
  - Better handling of MC / Order Interaction submit when no correct answers
    defined.

2.1.3:
  - Chunk file transfers to allow for seeking / streaming.

2.1.2:
  - Handle the case when no fileId label exists in question text,
    answer feedback, or choice.

2.1.1:
  - Remove redunant remove_choice method in records for inline choice.

2.1.0:
  - Maintain choice order for authoring-type endpoints.

2.0.0:
  - Switch to MongoDB backend.

1.11.1:
  - Fix bug with editing only item or question genusTypeId.

1.11.0:
  - Update dlkit; refactor internal calls for performance; enable memcache
    for qualifier ids.

1.10.0:
  - Update dlkit; remove some extraneous print statements.

1.9.0:
  - Refactor image URL handling so that item JSON returns right media paths.

1.8.7:
  - Update records for better error handling in getting asset file type
    config.

1.8.6:
  - Refactor asset creation to not hide underlying exceptions.

1.8.5:
  - Better handle non-qti items when using qti flag.

1.8.4:
  - Handle item QTI when no answers yet.

1.8.3:
  - Better unicode handling when wrapping text

1.8.2:
  - Allow questions to not have choices (fitb, mw, mc, reflection).

1.8.1:
  - Fix issue with updating choiceIds on answers, to replace instead of append.

1.8.0:
  - Add ability to get wrong answers for item list and assessment items list.

1.7.1:
  - Fix bug with newly created asset contents via JSON -- set them to be
      multi-language by default.

1.7.0:
  - Set the data store path for streaming asset contents to a configuration
      setting.

1.6.0:
  - Allow you to set the choice order for fill-in-the-blank,
      reflection, multiple-choice, moveable words, and image-sequence.

1.5.0:
  - Allow you to delete an item's existing choice.

1.4.0:
  - Allow you to delete an item's existing answer.

1.3.1:
  - Allow you to add a question during item update, when question in null on create.

1.3.0:
  - Update dlkit / primordium dependency

1.2.1:
  - Add endpoints for creating asset contents.
  - Improve unicode / hindi support

[3.16.4]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.16.3...v3.16.4
[3.16.3]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.16.2...v3.16.3
[3.16.2]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.16.1...v3.16.2
[3.16.1]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.16.0...v3.16.1
[3.16.0]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.15.11...v3.16.0
[3.15.11]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.15.10...v3.15.11
[3.15.10]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.15.9...v3.15.10
[3.15.9]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.15.8...v3.15.9
[3.15.8]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.15.7...v3.15.8
[3.15.7]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.15.6...v3.15.7
[3.15.6]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.15.5...v3.15.6
[3.15.5]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.15.4...v3.15.5
[3.15.4]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.15.3...v3.15.4
[3.15.3]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.15.2...v3.15.3
[3.15.2]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.15.1...v3.15.2
[3.15.1]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.15.0...v3.15.1
[3.15.0]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.14.10...v3.15.0
[3.14.10]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.14.9...v3.14.10
[3.14.9]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.14.8...v3.14.9
[3.14.8]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.14.7...v3.14.8
[3.14.7]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.14.6...v3.14.7
[3.14.6]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.14.5...v3.14.6
[3.14.5]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.14.4...v3.14.5
[3.14.4]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.14.3...v3.14.4
[3.14.3]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.14.2...v3.14.3
[3.14.2]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.14.1...v3.14.2
[3.14.1]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.14.0...v3.14.1
[3.14.0]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.13.1...v3.14.0
[3.13.1]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.13.0...v3.13.1
[3.13.0]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.12.0...v3.13.0
[3.12.0]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.11.6...v3.12.0
[3.11.6]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.11.5...v3.11.6
[3.11.5]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.11.4...v3.11.5
[3.11.4]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.11.3...v3.11.4
[3.11.3]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.11.2...v3.11.3
[3.11.2]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.11.1...v3.11.2
[3.11.1]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.11.0...v3.11.1
[3.11.0]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.10.0...v3.11.0
[3.10.0]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.9.2...v3.10.0
[3.9.2]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.9.1...v3.9.2
[3.9.1]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.9.0...v3.9.1
[3.9.0]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.8.6...v3.9.0
[3.8.6]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.8.5...v3.8.6
[3.8.5]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.8.4...v3.8.5
[3.8.4]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.8.3...v3.8.4
[3.8.3]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.8.2...v3.8.3
[3.8.2]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.8.1...v3.8.2
[3.8.1]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.8.0...v3.8.1
[3.8.0]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.7.7...v3.8.0
[3.7.7]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.7.6...v3.7.7
[3.7.6]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.7.5...v3.7.6
[3.7.5]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.7.4...v3.7.5
[3.7.4]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.7.3...v3.7.4
[3.7.3]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.7.2...v3.7.3
[3.7.2]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.7.1...v3.7.2
[3.7.1]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.7.0...v3.7.1
[3.7.0]: https://github.com/CLIxIndia-Dev/qbank-lite/compare/v3.6.0...v3.7.0
