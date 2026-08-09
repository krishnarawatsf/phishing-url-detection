import os
import sys
import importlib
import pytest

def test_python_version():
    """TC0.1: Check Python version compatibility (Python 3.9+)"""
    assert sys.version_info >= (3, 9), f"Python version must be >= 3.9, found {sys.version}"

def test_dependencies_importable():
    """TC0.1: Check all required dependencies import cleanly"""
    packages = ["pandas", "numpy", "sklearn", "joblib", "flask", "tldextract", "sqlite3", "pytest"]
    for pkg in packages:
        try:
            importlib.import_module(pkg)
        except ImportError as e:
            pytest.fail(f"Failed to import required package '{pkg}': {e}")

def test_directory_structure_exists():
    """TC0.2: Verify project directory layout"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    required_dirs = [
        os.path.join(base_dir, "core"),
        os.path.join(base_dir, "data", "raw"),
        os.path.join(base_dir, "data", "processed"),
        os.path.join(base_dir, "data", "models"),
        os.path.join(base_dir, "static", "css"),
        os.path.join(base_dir, "static", "js"),
        os.path.join(base_dir, "templates"),
        os.path.join(base_dir, "tests"),
    ]
    for d in required_dirs:
        assert os.path.exists(d) and os.path.isdir(d), f"Required directory missing: {d}"

def test_config_import():
    """TC0.3: Verify config module can be imported and paths are resolved"""
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import config
    assert hasattr(config, "RAW_DATASET_PATH")
    assert hasattr(config, "MODEL_PATH")
    assert hasattr(config, "RANDOM_STATE")
    assert config.RANDOM_STATE == 42
