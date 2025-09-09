from typing import Dict, Optional, List
from dataclasses import dataclass

@dataclass
class ProcessingResult:
    # You can define the structure of a processing result here
    result_data: dict

class ProcessingResultsManager:
    def __init__(self):
        self._results: Dict[str, ProcessingResult] = {}

    def store_result(self, image_path: str, result: ProcessingResult):
        """Stores a processing result for a given image path."""
        self._results[image_path] = result

    def get_result(self, image_path: str) -> Optional[ProcessingResult]:
        """Retrieves the processing result for a given image path."""
        return self._results.get(image_path)

    def get_all_results(self) -> Dict[str, ProcessingResult]:
        """Retrieves all stored processing results."""
        return self._results

    def clear_results(self):
        """Clears all stored processing results."""
        self._results.clear()

    def export_results(self, format: str) -> str:
        """Exports the results in a specified format (e.g., JSON, CSV)."""
        # This is a placeholder for export logic
        if format.lower() == 'json':
            import json
            # Handle both ProcessingResult objects and raw dicts
            export_data = {}
            for path, res in self._results.items():
                if hasattr(res, 'result_data'):
                    export_data[path] = res.result_data
                else:
                    export_data[path] = res
            return json.dumps(export_data, indent=4)
        elif format.lower() == 'csv':
            # Placeholder for CSV export
            csv_lines = ["image_path,result"]
            for path, res in self._results.items():
                result_data = res.result_data if hasattr(res, 'result_data') else res
                csv_lines.append(f'{path},{result_data}')
            return "\n".join(csv_lines)
        return "Unsupported format"
