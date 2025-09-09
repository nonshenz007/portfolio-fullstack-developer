
from typing import Callable, Optional
from core.processing_api import ProcessingAPI, ProcessingProgress

class UIProcessingBridge:
    def __init__(self, processing_api: ProcessingAPI):
        self.api = processing_api
        self.progress_update_callback: Optional[Callable[[ProcessingProgress], None]] = None
        self.error_display_callback: Optional[Callable[[str, str], None]] = None

        # Set up the API to call our bridge methods
        self.api.set_progress_callback(self.handle_progress_update)

    def set_progress_update_callback(self, callback: Callable[[ProcessingProgress], None]):
        """Register a callback function to handle progress updates in the UI."""
        self.progress_update_callback = callback

    def set_error_display_callback(self, callback: Callable[[str, str], None]):
        """Register a callback function to display errors in the UI."""
        self.error_display_callback = callback

    def handle_progress_update(self, progress: ProcessingProgress):
        """Receives progress from the backend and forwards it to the UI."""
        if self.progress_update_callback:
            self.progress_update_callback(progress)

    def handle_error(self, error_type: str, message: str):
        """Receives an error and forwards it to the UI for display."""
        if self.error_display_callback:
            # Here you might convert a technical error message to a user-friendly one
            user_message = self._convert_error_to_user_friendly_message(message)
            self.error_display_callback(error_type, user_message)

    # You can add more methods here to link other UI actions to the ProcessingAPI
    # For example, a method to start a batch process that is called by a UI button click
