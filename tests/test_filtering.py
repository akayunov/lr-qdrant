from qdrant_client import models
from qdrant_client.http.models import Record


async def test_filtering(async_client, collection, collection_name):
    payloads = [
        {"id": 1, "city": "London", "color": "green"},
        {"id": 2, "city": "London", "color": "red"},
        {"id": 3, "city": "London", "color": "blue"},
        {"id": 4, "city": "Berlin", "color": "red"},
        {"id": 5, "city": "Moscow", "color": "green"},
        {"id": 6, "city": "Moscow", "color": "blue"},
    ]

    v1 = [1, 1, 1]
    points = []
    for index, payload in enumerate(payloads):
        points.append(models.PointStruct(id=index + 1, vector=[*v1, index], payload=payload))

    await async_client.upsert(
        collection_name,
        points=points,
    )
    points = await async_client.scroll(
        collection_name,
        scroll_filter=models.Filter(
            must=[
                models.FieldCondition(key="city", match=models.MatchValue(value="London")),
                models.FieldCondition(key="color", match=models.MatchValue(value="red")),
            ]
        ),
    )
    assert points == (
        [
            Record(
                id=2, payload={"id": 2, "city": "London", "color": "red"}, vector=None, shard_key=None, order_value=None
            ),
        ],
        None,
    )

    points = await async_client.scroll(
        collection_name,
        scroll_filter=models.Filter(
            should=[
                models.FieldCondition(key="city", match=models.MatchValue(value="London")),
                models.FieldCondition(key="color", match=models.MatchValue(value="red")),
            ]
        ),
    )
    assert points == (
        [
            Record(id=1, payload={'id': 1, 'city': 'London', 'color': 'green'}, vector=None, shard_key=None, order_value=None),
            Record(
                id=2, payload={"id": 2, "city": "London", "color": "red"}, vector=None, shard_key=None, order_value=None
            ),
            Record(id=3, payload={'id': 3, 'color': 'blue', 'city': 'London'}, vector=None, shard_key=None, order_value=None),
            Record(id=4, payload={'city': 'Berlin', 'id': 4, 'color': 'red'}, vector=None, shard_key=None,
                   order_value=None),
        ],
        None,
    )

    points = await async_client.scroll(
        collection_name,
        scroll_filter=models.Filter(
            must_not=[
                models.Filter(
                    must=[models.FieldCondition(
                        key="city", match=models.MatchValue(value="London")
                    ),
                    models.FieldCondition(
                        key="color", match=models.MatchValue(value="red")
                    ),
                    ]
                ),
            ]
        ),
    )
    assert points == (
        [
            Record(id=1, payload={'id': 1, 'city': 'London', 'color': 'green'}, vector=None, shard_key=None, order_value=None),
            Record(id=3, payload={'city': 'London', 'id': 3, 'color': 'blue'}, vector=None, shard_key=None,
                   order_value=None),
            Record(id=4, payload={'city': 'Berlin', 'id': 4, 'color': 'red'}, vector=None, shard_key=None,
                   order_value=None),
            Record(id=5, payload={'city': 'Moscow', 'id': 5, 'color': 'green'}, vector=None, shard_key=None,
                   order_value=None),
            Record(id=6, payload={'city': 'Moscow', 'id': 6, 'color': 'blue'}, vector=None, shard_key=None,
                   order_value=None),
        ],
        None,
    )