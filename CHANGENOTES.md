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
