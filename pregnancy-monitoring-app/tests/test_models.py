import pytest

from app import create_app, db
from app.models import User


def test_import_models():
    # Basic smoke test: ensure models import without errors
    assert User is not None
