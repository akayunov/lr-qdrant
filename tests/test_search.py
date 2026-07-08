import random

from qdrant_client import models
from qdrant_client.http.models import Distance


async def test_search(async_client, collection, collection_name):
    v1 = [1, 1, 1, 1]
    v2 = [1, 2, 2, 4]
    await async_client.upsert(
        collection_name,
        points=[
            models.PointStruct(id=1, vector=v1),
            models.PointStruct(id=2, vector=[1, 2, 3, 4]),
            models.PointStruct(id=3, vector=v2),
        ],
    )

    points = await async_client.query_points(collection_name, query=1)  # similar to vector with id == 1
    assert (len(points.points)) == 2
    assert points.points[0].id == 2
    assert points.points[1].id == 3

    points = await async_client.query_points(collection_name, query=v2)  # similar to this vector
    assert (len(points.points)) == 3
    # вектор длинный поэтому попал на первое место, используется метрика DOT а не COS
    # если нормировать вектора то 3 -й вектор будет первым
    assert points.points[0].id == 2
    assert points.points[1].id == 3
    assert points.points[2].id == 1

    cos_collection_name = f"test_collection_cosin_{random.randint(0, 1_000_000)}"
    await async_client.create_collection(
        collection_name=cos_collection_name,
        vectors_config={"size": 4, "distance": Distance.COSINE},
    )
    # нормировка идет автоматом
    await async_client.upsert(
        cos_collection_name,
        points=[
            models.PointStruct(id=1, vector=v1),
            models.PointStruct(id=2, vector=[1, 2, 3, 4]),
            models.PointStruct(id=3, vector=v2),
        ],
    )
    points = await async_client.query_points(cos_collection_name, query=v2)  # similar to this vector
    assert (len(points.points)) == 3
    assert points.points[0].id == 3
    assert points.points[1].id == 2
    assert points.points[2].id == 1
