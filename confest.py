import pytest
from PySide6.QtWidgets import QApplication
from unittest.mock import MagicMock

@pytest.fixture(scope="session")
def qt_app():
    """Фикстура для QApplication"""
    app = QApplication.instance() or QApplication([])
    yield app
    app.quit()

@pytest.fixture
def db_mock():
    """Фикстура для мока базы данных"""
    return MagicMock()