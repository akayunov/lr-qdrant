import uuid

import pytest
from qdrant_client import models
from qdrant_client.http.models import Record, UpdateMode, SparseVector, QueryResponse, ScoredPoint


def test_points(client, collection, collection_name):
    v1 = [1, 1, 1, 1]
    v2 = [1, 2, 3, 4]
    client.upsert(
        collection_name,
        points=[
            models.PointStruct(id=1, payload={"color": "red"}, vector=v1),
            models.PointStruct(id=2, payload={"color": "yellow"}, vector=v1),
        ],
    )
    point_uuid = str(uuid.uuid4())
    client.upsert(
        collection_name,
        points=[
            models.PointStruct(id=point_uuid, payload={"color": "blue"}, vector=v2),
            models.PointStruct(id=point_uuid, payload={"color": "green"}, vector=v2),
        ],
    )

    points = client.retrieve(collection_name, ids=[1, 2, point_uuid], with_vectors=True)
    assert points == [
        Record(id=1, payload={"color": "red"}, vector=v1, shard_key=None, order_value=None),
        Record(id=2, payload={"color": "yellow"}, vector=v1, shard_key=None, order_value=None),
        Record(id=point_uuid, payload={"color": "green"}, vector=v2, shard_key=None, order_value=None),
    ]


async def test_batch_points(async_client, collection, collection_name):
    v1 = [1, 1, 1, 1]
    v2 = [1, 2, 3, 4]
    v3 = [4, 3, 2, 1]

    await async_client.upsert(
        collection_name,
        points=models.Batch(
            ids=(1, 2, 3), payloads=({"color": "red"}, {"color": "blue"}, {"color": "green"}), vectors=(v1, v2, v3)
        ),
    )

    points = await async_client.retrieve(collection_name, ids=[1, 2, 3], with_vectors=True)
    assert points == [
        Record(id=1, payload={"color": "red"}, vector=v1, shard_key=None, order_value=None),
        Record(id=2, payload={"color": "blue"}, vector=v2, shard_key=None, order_value=None),
        Record(id=3, payload={"color": "green"}, vector=v3, shard_key=None, order_value=None),
    ]


async def test_update(async_client, collection, collection_name):
    v1 = [1, 1, 1, 1]

    await async_client.upsert(
        collection_name,
        points=[
            models.PointStruct(id=1, payload={"color": "red"}, vector=v1),
        ],
    )
    points = await async_client.retrieve(collection_name, ids=[1], with_vectors=True)
    assert points == [
        Record(id=1, payload={"color": "red"}, vector=v1, shard_key=None, order_value=None),
    ]

    # standard upsert
    await async_client.upsert(
        collection_name,
        points=[
            models.PointStruct(id=1, payload={"color": "blue"}, vector=v1),
        ],
    )
    points = await async_client.retrieve(collection_name, ids=[1], with_vectors=True)
    assert points == [
        Record(id=1, payload={"color": "blue"}, vector=v1, shard_key=None, order_value=None),
    ]

    # insert_only upsert
    await async_client.upsert(
        collection_name,
        points=[
            models.PointStruct(id=1, payload={"color": "yellow"}, vector=v1),
        ],
        update_mode=UpdateMode.INSERT_ONLY,
    )
    points = await async_client.retrieve(collection_name, ids=[1], with_vectors=True)
    assert points == [
        Record(id=1, payload={"color": "blue"}, vector=v1, shard_key=None, order_value=None),
    ]

    # update_only upsert
    await async_client.upsert(
        collection_name,
        points=[
            models.PointStruct(id=2, payload={"color": "yellow"}, vector=v1),
        ],
        update_mode=UpdateMode.UPDATE_ONLY,
    )
    points = await async_client.retrieve(collection_name, ids=[2], with_vectors=True)
    assert points == []


@pytest.mark.parametrize(
    "collection",  # параметры для фикстуры collection
    [
        {
            "kwargs": {
                "vectors_config": {
                    "subvector1": models.VectorParams(size=4, distance=models.Distance.DOT),
                    "subvector2": models.VectorParams(size=4, distance=models.Distance.DOT),
                }
            }
        }
    ],
    indirect=True,
)
async def test_named_vector(async_client, collection, collection_name):
    v1 = [1, 1, 1, 1]
    v2 = [1, 2, 3, 4]

    await async_client.upsert(
        collection_name,
        points=[
            models.PointStruct(
                id=1,
                payload={"color": "red"},
                vector={
                    "subvector1": v1,
                    "subvector2": v2,
                },
            ),
        ],
    )

    points = await async_client.retrieve(collection_name, ids=[1], with_vectors=True)
    assert points == [
        Record(
            id=1,
            payload={"color": "red"},
            vector={
                "subvector1": v1,
                "subvector2": v2,
            },
            shard_key=None,
            order_value=None,
        ),
    ]

    points = await async_client.query_points(collection_name, query=v1, using="subvector1", with_vectors=True)
    assert points == QueryResponse(
        points=[
            ScoredPoint(
                id=1,
                version=1,
                score=4.0,
                payload={"color": "red"},
                vector={"subvector1": [1.0, 1.0, 1.0, 1.0], "subvector2": [1.0, 2.0, 3.0, 4.0]},
                shard_key=None,
                order_value=None,
            )
        ]
    )
    points = await async_client.query_points(collection_name, query=v1, using="subvector2", with_vectors=True)
    assert points == QueryResponse(
        points=[
            ScoredPoint(
                id=1,
                version=1,
                score=10.0,
                payload={"color": "red"},
                vector={"subvector1": [1.0, 1.0, 1.0, 1.0], "subvector2": [1.0, 2.0, 3.0, 4.0]},
                shard_key=None,
                order_value=None,
            )
        ]
    )


@pytest.mark.parametrize(
    "collection",
    [
        {
            "kwargs": {  # у нас будет разреженный вектор с именем "sparce_text_verctor"
                "sparse_vectors_config": {"sparce_text_verctor": models.SparseVectorParams()},
                # Так как этот тест только для sparse-векторов, отключаем дефолтный плотный вектор
                "vectors_config": {},
            }
        }
    ],
    indirect=True,
)
async def test_sparse_vector(async_client, collection, collection_name):
    await async_client.upsert(
        collection_name,
        points=[
            models.PointStruct(
                id=1,
                payload={"color": "red"},
                vector={
                    "sparce_text_verctor": models.SparseVector(indices=[5, 4, 3, 1, 2], values=[55, 44, 33, 11, 22])
                },
            ),
        ],
    )

    points = await async_client.retrieve(collection_name, ids=[1], with_vectors=True)
    assert points == [
        Record(
            id=1,
            payload={"color": "red"},
            vector={
                "sparce_text_verctor": SparseVector(indices=[1, 2, 3, 4, 5], values=[11.0, 22.0, 33.0, 44.0, 55.0])
            },
            shard_key=None,
            order_value=None,
        ),
    ]


async def test_update_vector(async_client, collection, collection_name):
    v1 = [1, 1, 1, 1]
    v2 = [1, 2, 3, 4]
    await async_client.upsert(collection_name, points=[models.PointStruct(id=1, payload={"color": "red"}, vector=v1)])
    await async_client.upsert(collection_name, points=[models.PointStruct(id=2, payload={"color": "red"}, vector=v1)])

    await async_client.update_vectors(collection_name, points=[models.PointVectors(id=1, vector=v2)])
    await async_client.update_vectors(collection_name, points=[models.PointVectors(id=2, vector=v1)])

    points = await async_client.retrieve(collection_name, ids=[1, 2], with_vectors=True)
    assert points == [
        Record(id=1, payload={"color": "red"}, vector=v2, shard_key=None, order_value=None),
        Record(id=2, payload={"color": "red"}, vector=v1, shard_key=None, order_value=None),
    ]


@pytest.mark.parametrize(
    "collection",  # параметры для фикстуры collection
    [
        {
            "kwargs": {
                "vectors_config": {
                    "subvector1": models.VectorParams(size=4, distance=models.Distance.DOT),
                    "subvector2": models.VectorParams(size=4, distance=models.Distance.DOT),
                }
            }
        }
    ],
    indirect=True,
)
async def test_delete_vector(async_client, collection, collection_name):
    v1 = [1, 1, 1, 1]
    v2 = [1, 2, 3, 4]

    await async_client.upsert(
        collection_name,
        points=[
            models.PointStruct(
                id=1,
                payload={"color": "red"},
                vector={
                    "subvector1": v1,
                    "subvector2": v2,
                },
            ),
        ],
    )

    await async_client.delete_vectors(collection_name, points=[1], vectors=["subvector1"])

    points = await async_client.retrieve(collection_name, ids=[1], with_vectors=True)
    assert points == [
        Record(
            id=1,
            payload={"color": "red"},
            vector={"subvector2": [1.0, 2.0, 3.0, 4.0]},
            shard_key=None,
            order_value=None,
        ),
    ]


async def test_delete_points(async_client, collection, collection_name):
    v1 = [1, 1, 1, 1]
    await async_client.upsert(collection_name, points=[models.PointStruct(id=1, payload={"color": "red"}, vector=v1)])

    point = await async_client.retrieve(collection_name, ids=[1], with_vectors=True)
    assert point == [
        Record(id=1, payload={"color": "red"}, vector=v1, shard_key=None, order_value=None),
    ]

    await async_client.delete(collection_name, points_selector=models.PointIdsList(points=[1]))
    point = await async_client.retrieve(collection_name, ids=[1], with_vectors=True)
    assert point == []

    # with selector
    v2 = [1, 2, 3, 4]
    await async_client.upsert(collection_name, points=[models.PointStruct(id=2, payload={"color": "blue"}, vector=v2)])

    point = await async_client.retrieve(collection_name, ids=[2], with_vectors=True)
    assert point == [
        Record(id=2, payload={"color": "blue"}, vector=v2, shard_key=None, order_value=None),
    ]

    await async_client.delete(
        collection_name,
        points_selector=models.FilterSelector(
            filter=models.Filter(must=[models.FieldCondition(key="color", match=models.MatchValue(value="blue"))]),
        ),
    )
    point = await async_client.retrieve(collection_name, ids=[2], with_vectors=True)
    assert point == []


async def test_conditional_update(async_client, collection, collection_name):
    v1 = [1, 1, 1, 1]
    await async_client.upsert(collection_name, points=[models.PointStruct(id=1, payload={"color": "red"}, vector=v1)])
    v2 = [1, 2, 3, 4]
    await async_client.upsert(
        collection_name,
        points=[models.PointStruct(id=1, payload={"color": "blue"}, vector=v2)],
        update_filter=models.Filter(
            must=models.FieldCondition(key="color", match=models.MatchValue(value="somethingother"))
        ),
    )

    points = await async_client.retrieve(collection_name, ids=[1], with_vectors=True)
    assert points == [
        Record(id=1, payload={"color": "red"}, vector=v1, shard_key=None, order_value=None),
    ]


async def test_scroll_points(async_client, collection, collection_name):
    v1 = [1, 1, 1, 1]
    v2 = [1, 2, 3, 4]
    await async_client.upsert(
        collection_name,
        points=[
            models.PointStruct(id=1, payload={"color": "red"}, vector=v1),
            models.PointStruct(id=2, payload={"color": "red"}, vector=v2),
        ],
    )

    points = await async_client.scroll(
        collection_name,
        scroll_filter=models.Filter(must=[models.FieldCondition(key="color", match=models.MatchValue(value="red"))]),
        limit=1,
    )
    assert points == (
        [
            Record(id=1, payload={"color": "red"}, vector=None, shard_key=None, order_value=None),
        ],
        2,
    )
