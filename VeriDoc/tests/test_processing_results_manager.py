
import unittest
import json
from core.processing_results_manager import ProcessingResultsManager, ProcessingResult

class TestProcessingResultsManager(unittest.TestCase):

    def setUp(self):
        self.manager = ProcessingResultsManager()
        self.result1 = ProcessingResult(result_data={"status": "pass"})
        self.result2 = ProcessingResult(result_data={"status": "fail"})
        self.image_path1 = "/path/to/image1.jpg"
        self.image_path2 = "/path/to/image2.png"

    def test_store_and_get_result(self):
        self.manager.store_result(self.image_path1, self.result1)
        retrieved_result = self.manager.get_result(self.image_path1)
        self.assertEqual(retrieved_result, self.result1)
        self.assertIsNone(self.manager.get_result("non_existent_path"))

    def test_get_all_results(self):
        self.manager.store_result(self.image_path1, self.result1)
        self.manager.store_result(self.image_path2, self.result2)
        all_results = self.manager.get_all_results()
        self.assertEqual(len(all_results), 2)
        self.assertEqual(all_results[self.image_path1], self.result1)

    def test_clear_results(self):
        self.manager.store_result(self.image_path1, self.result1)
        self.manager.clear_results()
        self.assertEqual(len(self.manager.get_all_results()), 0)

    def test_export_results_json(self):
        self.manager.store_result(self.image_path1, self.result1)
        self.manager.store_result(self.image_path2, self.result2)
        json_export = self.manager.export_results('json')
        expected_dict = {
            self.image_path1: self.result1.result_data,
            self.image_path2: self.result2.result_data
        }
        self.assertEqual(json.loads(json_export), expected_dict)

    def test_export_results_csv(self):
        self.manager.store_result(self.image_path1, self.result1)
        csv_export = self.manager.export_results('csv')
        self.assertIn("image_path,result", csv_export)
        self.assertIn(self.image_path1, csv_export)

    def test_export_results_unsupported_format(self):
        self.assertEqual(self.manager.export_results('xml'), "Unsupported format")

if __name__ == '__main__':
    unittest.main()
