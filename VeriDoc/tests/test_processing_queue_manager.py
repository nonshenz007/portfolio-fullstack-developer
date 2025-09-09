
import unittest
from core.processing_queue_manager import ProcessingQueueManager, QueueStatus

class TestProcessingQueueManager(unittest.TestCase):

    def setUp(self):
        self.manager = ProcessingQueueManager()
        self.image_paths = ["/path/to/image1.jpg", "/path/to/image2.png"]

    def test_add_images(self):
        self.manager.add_images(self.image_paths)
        self.assertEqual(self.manager.get_queue_status().total_items, 2)
        self.manager.add_images(["/path/to/image1.jpg"]) # Test adding existing
        self.assertEqual(self.manager.get_queue_status().total_items, 2)

    def test_remove_image(self):
        self.manager.add_images(self.image_paths)
        self.manager.remove_image("/path/to/image1.jpg")
        self.assertEqual(self.manager.get_queue_status().total_items, 1)
        self.assertEqual(self.manager.get_queue_status().pending_items, 1)

    def test_clear_queue(self):
        self.manager.add_images(self.image_paths)
        self.manager.clear_queue()
        self.assertEqual(self.manager.get_queue_status().total_items, 0)

    def test_get_queue_status(self):
        self.manager.add_images(self.image_paths)
        status = self.manager.get_queue_status()
        self.assertIsInstance(status, QueueStatus)
        self.assertEqual(status.total_items, 2)
        self.assertEqual(status.pending_items, 2)
        self.assertEqual(status.processed_items, 0)
        self.assertFalse(status.is_processing)

    def test_process_next(self):
        self.manager.add_images(self.image_paths)
        result = self.manager.process_next()
        self.assertIsNotNone(result)
        self.assertEqual(self.manager.get_queue_status().processed_items, 1)
        self.assertEqual(self.manager.get_queue_status().pending_items, 1)

    def test_process_all(self):
        self.manager.add_images(self.image_paths)
        self.manager.process_all(format_name="ICS-UAE")
        self.assertEqual(self.manager.get_queue_status().processed_items, 2)
        self.assertEqual(self.manager.get_queue_status().pending_items, 0)

if __name__ == '__main__':
    unittest.main()
