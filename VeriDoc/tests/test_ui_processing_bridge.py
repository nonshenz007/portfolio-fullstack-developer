
import unittest
from unittest.mock import MagicMock, Mock
from core.processing_api import ProcessingAPI, ProcessingProgress
from ui.ui_processing_bridge import UIProcessingBridge

class TestUIProcessingBridge(unittest.TestCase):

    def setUp(self):
        # Mock the ProcessingAPI
        self.mock_api = Mock(spec=ProcessingAPI)
        # Instantiate the bridge with the mocked API
        self.bridge = UIProcessingBridge(self.mock_api)

    def test_initialization(self):
        # Check if the bridge's API attribute is set correctly
        self.assertEqual(self.bridge.api, self.mock_api)
        # Check if the API's progress callback is set to the bridge's handler
        self.mock_api.set_progress_callback.assert_called_with(self.bridge.handle_progress_update)

    def test_set_progress_update_callback(self):
        # Create a mock callback function
        mock_callback = MagicMock()
        # Set the callback on the bridge
        self.bridge.set_progress_update_callback(mock_callback)
        # Check if the callback is stored correctly
        self.assertEqual(self.bridge.progress_update_callback, mock_callback)

    def test_handle_progress_update(self):
        # Create a mock callback and set it
        mock_callback = MagicMock()
        self.bridge.set_progress_update_callback(mock_callback)
        # Create a dummy progress object
        progress = ProcessingProgress(stage="testing", progress_percent=50, message="in progress")
        # Call the handler
        self.bridge.handle_progress_update(progress)
        # Assert that the UI callback was called with the progress object
        mock_callback.assert_called_with(progress)

    def test_set_error_display_callback(self):
        mock_callback = MagicMock()
        self.bridge.set_error_display_callback(mock_callback)
        self.assertEqual(self.bridge.error_display_callback, mock_callback)

    def test_handle_error(self):
        mock_callback = MagicMock()
        self.bridge.set_error_display_callback(mock_callback)
        error_type = "File Error"
        technical_message = "file not found"
        user_message = self.bridge._convert_error_to_user_friendly_message(technical_message)
        
        self.bridge.handle_error(error_type, technical_message)
        
        mock_callback.assert_called_with(error_type, user_message)

    def test_convert_error_to_user_friendly_message(self):
        technical_message = "some technical detail"
        expected_message = f"An unexpected error occurred: {technical_message}"
        self.assertEqual(self.bridge._convert_error_to_user_friendly_message(technical_message), expected_message)

if __name__ == '__main__':
    unittest.main()
