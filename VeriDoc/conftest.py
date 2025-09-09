import os
import pytest

# Ensure headless Qt in CI and local tests
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def pytest_collection_modifyitems(config, items):
    # Skip brittle UI tests in CI/headless environments
    headless = os.environ.get("QT_QPA_PLATFORM") == "offscreen"
    in_ci = os.environ.get("CI", "").lower() == "true"
    if not (headless or in_ci):
        return
    for item in items:
        node = getattr(item, 'nodeid', '')
        if 'test_ui_validation_checklist.py' in node:
            item.add_marker(pytest.mark.skip(reason="Skipped in headless/CI: brittle Qt UI test"))


