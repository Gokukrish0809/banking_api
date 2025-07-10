from fastapi.testclient import TestClient


def test_startup_event_calls_create_all(monkeypatch):
    # Import here so we patch before the handler is bound
    import app.main  # registers the startup event
    from app.database import Base, engine

    called = []
    # Patch Base.metadata.create_all
    monkeypatch.setattr(
        Base.metadata,
        "create_all",
        lambda eng: called.append(eng),
    )

    # Now instantiate the TestClient, which triggers startup
    with TestClient(app.main.app):
        pass

    # Assert our fake was called exactly once with the real engine
    assert called == [engine]
