from testing_utilities import BaseTestCase


class BaseDragAndDropTestCase(BaseTestCase):
    @staticmethod
    def _item_payload():
        """payload without the question and answer parts.
        Pull in self._question_payload() and self._answers_payload() if you need those"""
        return {}

    @staticmethod
    def _question_payload():
        return {}

    @staticmethod
    def _answers_payload():
        return []

    def create_item_without_question_or_answers(self):
        pass

    def create_item_with_question_and_answers(self):
        pass

    def setUp(self):
        super(BaseDragAndDropTestCase, self).setUp()

    def tearDown(self):
        super(BaseDragAndDropTestCase, self).tearDown()


def CreateTests(BaseDragAndDropTestCase):
    """Can create drag and drop RESTfully"""
    def test_can_create_item_with_question(self):
        """Make sure question genusTypeId is set properly"""
        self.fail('finish writing the test')

    def test_can_create_item_without_question(self):
        self.fail('finish writing the test')

    def test_can_create_item_with_answers(self):
        """ make sure the answer records are right
        """
        self.fail('finish writing the test')

    def test_can_set_zones_in_question(self):
        self.fail('finish writing the test')

    def test_can_set_droppables_in_question(self):
        self.fail('finish writing the test')

    def test_can_set_targets_in_question(self):
        self.fail('finish writing the test')

    def test_can_create_question_with_files(self):
        self.fail('finish writing the test')

    def test_can_create_answers_with_files(self):
        self.fail('finish writing the test')

    def test_getting_item_with_files_returns_right_source_urls(self):
        self.fail('finish writing the test')

    def test_can_set_shuffle_droppables_flag(self):
        self.fail('finish writing the test')

    def test_can_set_shuffle_targets_flag(self):
        self.fail('finish writing the test')

    def test_shuffled_droppables_do_not_shuffle_for_authoring(self):
        self.fail('finish writing the test')

    def test_shuffled_targets_do_not_shuffle_for_authoring(self):
        self.fail('finish writing the test')


def UpdateTests(BaseDragAndDropTestCase):
    """Can edit the drag and drop RESTfully"""
    def test_can_add_question_to_existing_item(self):
        self.fail('finish writing the test')

    def test_can_add_answers_to_existing_item(self):
        self.fail('finish writing the test')

    def test_can_update_zone_with_new_language(self):
        self.fail('finish writing the test')

    def test_can_remove_zone_language(self):
        self.fail('finish writing the test')

    def test_can_add_new_zone(self):
        self.fail('finish writing the test')

    def test_can_remove_zone(self):
        self.fail('finish writing the test')

    def test_can_clear_zone_texts(self):
        self.fail('finish writing the test')

    def test_can_update_target_with_new_language(self):
        self.fail('finish writing the test')

    def test_can_remove_target_language(self):
        self.fail('finish writing the test')

    def test_can_add_new_target(self):
        self.fail('finish writing the test')

    def test_can_remove_target(self):
        self.fail('finish writing the test')

    def test_can_clear_target_texts(self):
        self.fail('finish writing the test')

    def test_can_update_droppable_with_new_language(self):
        self.fail('finish writing the test')

    def test_can_remove_droppable_language(self):
        self.fail('finish writing the test')

    def test_can_add_new_droppable(self):
        self.fail('finish writing the test')

    def test_can_remove_droppable(self):
        self.fail('finish writing the test')

    def test_can_clear_droppable_texts(self):
        self.fail('finish writing the test')

    def test_can_add_new_file_to_question(self):
        self.fail('finish writing the test')

    def test_can_turn_shuffle_droppables_off(self):
        self.fail('finish writing the test')

    def test_can_turn_shuffle_droppables_on(self):
        self.fail('finish writing the test')

    def test_can_turn_shuffle_targets_on(self):
        self.fail('finish writing the test')

    def test_can_turn_shuffle_targets_off(self):
        self.fail('finish writing the test')


def DeleteTests(BaseDragAndDropTestCase):
    """Can delete various parts RESTfully"""
    def test_can_delete_drag_and_drop_item(self):
        self.fail('finish writing the test')


def TakingTests(BaseDragAndDropTestCase):
    """Can submit right / wrong answers to a drag-and-drop question"""
    def test_shuffled_droppables_do_shuffle_when_taking(self):
        self.fail('finish writing the test')

    def test_shuffled_targets_do_shuffle_when_taking(self):
        self.fail('finish writing the test')

    def test_can_submit_wrong_answer(self):
        self.fail('finish writing the test')

    def test_can_submit_right_answer(self):
        self.fail('finish writing the test')