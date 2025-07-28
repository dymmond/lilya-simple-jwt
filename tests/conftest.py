import pytest
from lilya.apps import Lilya
from lilya.conf import settings
from lilya.routing import Include
from lilya.testclient import TestClient

database, models = settings.edgy_registry


def create_app():
    from edgy import Instance, monkay

    # ensure the settings are loaded
    monkay.evaluate_settings(
        ignore_preload_import_errors=False,
        onetime=False,
    )
    app = Lilya(routes=[Include(path="/simple-jwt", namespace="lilya_simple_jwt.urls")])
    monkay.set_instance(Instance(registry=app.settings.registry, app=app))
    return app


def get_client():
    return TestClient(create_app())


@pytest.fixture(scope="module")
def anyio_backend():
    return ("asyncio", {"debug": False})


@pytest.fixture
def app():
    return create_app()


@pytest.fixture(autouse=True, scope="function")
async def create_test_database():
    async with models.database:
        await models.create_all()
        yield
        if not models.database.drop:
            await models.drop_all()


@pytest.fixture(autouse=True, scope="function")
async def rollback_transactions():
    async with models.database:
        yield
