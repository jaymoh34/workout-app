import os

# Use an in-memory database for tests; must be set before app is imported.
os.environ["DATABASE_URI"] = "sqlite:///:memory:"

import pytest

from app import app as flask_app
from models import db


@pytest.fixture()
def client():
    with flask_app.app_context():
        db.create_all()
        yield flask_app.test_client()
        db.session.remove()
        db.drop_all()
