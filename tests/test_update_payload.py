from qdrant_client import models
from qdrant_client.http.models import Record


async def test_update_payload(async_client, collection, collection_name):
    payload = {"colour": "red"}
    await async_client.upsert(collection_name, points=[models.PointStruct(id=1, payload=payload, vector=[1, 1, 1, 1])])
    await async_client.set_payload(collection_name, payload={"shape": "romb"}, points=[1])
    points = await async_client.retrieve(collection_name, ids=[1])
    assert points == [
        Record(id=1, payload={"colour": "red", "shape": "romb"}, vector=None, shard_key=None, order_value=None),
    ]

    await async_client.set_payload(
        collection_name,
        payload={"shape": "square"},
        points=models.Filter(must=[models.FieldCondition(key="shape", match=models.MatchValue(value="romb"))]),
    )
    points = await async_client.retrieve(collection_name, ids=[1])
    assert points == [
        Record(id=1, payload={"colour": "red", "shape": "square"}, vector=None, shard_key=None, order_value=None),
    ]

    await async_client.overwrite_payload(collection_name, payload={"quality": "bad"}, points=[1])
    points = await async_client.retrieve(collection_name, ids=[1])
    assert points == [
        Record(id=1, payload={"quality": "bad"}, vector=None, shard_key=None, order_value=None),
    ]

    await async_client.clear_payload(collection_name, points_selector=[1])
    points = await async_client.retrieve(collection_name, ids=[1])
    assert points == [
        Record(id=1, payload={}, vector=None, shard_key=None, order_value=None),
    ]
