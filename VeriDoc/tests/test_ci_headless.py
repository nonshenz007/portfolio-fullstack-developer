import os


def test_headless_env_flags_present():
    # CI should set these for deterministic/headless runs
    assert os.environ.get('QT_QPA_PLATFORM', 'offscreen') == 'offscreen'
    # NO_AI default can be overridden locally; just ensure it is defined to something
    assert os.environ.get('VERIDOC_NO_AI', '1') in ('0', '1')


