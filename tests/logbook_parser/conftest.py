"""conftest.py file for logbook_parser"""
import logging
from pathlib import Path
from importlib import resources

import pytest

from ..logging import rotating_file_logger

APP_LOG_LEVEL = logging.INFO
TEST_LOG_LEVEL = logging.DEBUG
# If PROJECT_NAMESPACE not used, then make PROJECT_NAMESPACE = ""
# PROJECT_NAMESPACE = "project_namespace".upper() + "_"
PROJECT_NAMESPACE = ""
PROJECT_SLUG = "logbook_parser".upper()


@pytest.fixture(scope="session")
def report_data_ctx():
    return resources.path("tests.logbook_parser.resources", "formatted_report.xml")


@pytest.fixture(scope="session", name="logger")
def _logger(test_log_path):
    """A central logger that will log to file."""
    # log_file_name = f"{__name__}.log"
    log_dir: Path = test_log_path / Path("test-logs")

    logger = rotating_file_logger(
        log_dir=log_dir, log_name=__name__, log_level=TEST_LOG_LEVEL
    )

    return logger


@pytest.fixture(scope="session", name="test_log_path")
def test_log_path_(test_app_data_dir) -> Path:
    """Make a test-log directory under the app data directory"""
    log_path = test_app_data_dir / Path("test-logs")
    print(f"Logging at: {log_path}")
    return log_path


@pytest.fixture(scope="session", name="test_app_data_dir")
def test_app_data_dir_(tmp_path_factory) -> Path:
    """make a temp directory for app data."""
    test_app_data_dir = tmp_path_factory.mktemp(PROJECT_SLUG.lower() + "-")
    return test_app_data_dir


@pytest.fixture(autouse=True)
def env_setup(monkeypatch, test_app_data_dir):
    """environment variables set for each test."""
    monkeypatch.setenv(
        PROJECT_NAMESPACE + PROJECT_SLUG + "_TESTING",
        "True",
    )
    monkeypatch.setenv(
        PROJECT_NAMESPACE + PROJECT_SLUG + "_LOG_LEVEL",
        str(APP_LOG_LEVEL),
    )
    monkeypatch.setenv(
        PROJECT_NAMESPACE + PROJECT_SLUG + "_APP_DIR",
        str(test_app_data_dir),
    )
