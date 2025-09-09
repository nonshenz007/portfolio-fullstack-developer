# Developer Guide

This guide provides an overview of the new processing pipeline components.

## ProcessingAPI

The `ProcessingAPI` class is the main entry point for all processing tasks. It provides a clean interface for the UI to interact with the backend.

### Key Methods

- `import_files(file_paths: List[str]) -> ImportResult`
- `import_folder(folder_path: str) -> ImportResult`
- `process_image(image_path: str, format_name: str) -> ProcessingResult`
- `process_all_queued() -> BatchProcessingResult`
- `auto_fix_image(image_path: str) -> AutoFixResult`
- `get_validation_results(image_path: str) -> ValidationResult`

## UIProcessingBridge

The `UIProcessingBridge` class acts as a bridge between the UI and the `ProcessingAPI`. It handles UI-specific tasks like progress updates and error handling.

### Key Methods

- `set_progress_update_callback(callback: Callable[[ProcessingProgress], None])`
- `set_error_display_callback(callback: Callable[[str, str], None])`
