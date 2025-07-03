import pytest
from sqlalchemy.orm import Session
import db.database as database

class DummySession:
    def __init__(self):
        self.closed = False
    def close(self):
        self.closed = True


def test_get_db_yields_real_session_and_closes():
    # Using the existing SessionLocal, get_db should yield a session and close it
    gen = database.get_db()
    sess = next(gen)
    # Should at least have a close method
    assert hasattr(sess, 'close') and callable(sess.close)
    # Closing the generator should trigger the finally block without error
    gen.close()


def test_get_db_uses_custom_sessionlocal_and_closes(monkeypatch):
    # Patch SessionLocal to return our DummySession
    monkeypatch.setattr(database, 'SessionLocal', lambda: DummySession())

    gen = database.get_db()
    sess = next(gen)
    # Should return our dummy
    assert isinstance(sess, DummySession)

    # Closing the generator should call DummySession.close()
    gen.close()
    assert sess.closed is True
