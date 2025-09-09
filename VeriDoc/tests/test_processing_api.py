
import unittest
from unittest.mock import MagicMock
from core.processing_api import ProcessingAPI, ImportResult, ProcessingResult, AutoFixResult, ValidationResult, BatchProcessingResult

class TestProcessingAPI(unittest.TestCase):

    def setUp(self):
        self.progress_callback = MagicMock()
        self.api = ProcessingAPI(progress_callback=self.progress_callback)

    def test_import_files(self):
        file_paths = ["/path/to/image1.jpg", "/path/to/image2.png"]
        result = self.api.import_files(file_paths)
        self.assertIsInstance(result, ImportResult)
        self.assertTrue(result.success)
        self.assertEqual(result.imported_count, len(file_paths))

    def test_import_folder(self):
        folder_path = "/path/to/folder"
        result = self.api.import_folder(folder_path)
        self.assertIsInstance(result, ImportResult)
        self.assertTrue(result.success)

    def test_process_image(self):
        image_path = "/path/to/image.jpg"
        result = self.api.process_image(image_path)
        self.assertIsInstance(result, ProcessingResult)

    def test_process_all_queued(self):
        result = self.api.process_all_queued()
        self.assertIsInstance(result, BatchProcessingResult)

    def test_auto_fix_image(self):
        image_path = "/path/to/image.jpg"
        result = self.api.auto_fix_image(image_path)
        self.assertIsInstance(result, AutoFixResult)

    def test_get_validation_results(self):
        image_path = "/path/to/image.jpg"
        result = self.api.get_validation_results(image_path)
        self.assertIsInstance(result, ValidationResult)

    def test_set_progress_callback(self):
        new_callback = MagicMock()
        self.api.set_progress_callback(new_callback)
        self.assertEqual(self.api.progress_callback, new_callback)

if __name__ == '__main__':
    unittest.main()
