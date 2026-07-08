import os
from random import randint

import pytest
from qdrant_client import QdrantClient, AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams


@pytest.fixture
def collection_name():
    return f"test_coll_{randint(1, 1_000_000)}"


@pytest.fixture
def qdrant_url():
    default_url = os.environ.get("QDRANT_URL", "")
    yield default_url


@pytest.fixture
def client(qdrant_url):
    return QdrantClient(url=qdrant_url)


@pytest.fixture
def async_client(qdrant_url):
    return AsyncQdrantClient(url=qdrant_url)


@pytest.fixture
def collection(client, collection_name, request):
    # Получаем параметры через request.param
    params = request.param if hasattr(request, "param") else {}
    kwargs = params.get("kwargs", {})
    vectors_config = kwargs.pop("vectors_config", {"size": 4, "distance": Distance.DOT})
    # Проверяем, именованные ли это векторы:
    if not vectors_config:
        # Если vectors_config пришел пустым ({}) или None, передаем None в Qdrant
        final_vectors_config = None
    else:
        # Проверяем, именованные ли это векторы
        is_named_vectors = isinstance(vectors_config, dict) and any(
            isinstance(v, (VectorParams, dict)) for v in vectors_config.values()
        )

        if is_named_vectors:
            # Для именованных векторов передаем словарь как есть
            final_vectors_config = vectors_config
        else:
            # Для одиночного вектора собираем VectorParams
            final_vectors_config = VectorParams(**vectors_config)

    client.create_collection(
        collection_name=collection_name,
        vectors_config=final_vectors_config,
        **kwargs,
    )
    yield
    client.delete_collection(collection_name=collection_name)
