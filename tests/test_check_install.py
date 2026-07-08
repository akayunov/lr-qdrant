from qdrant_client.models import Filter, FieldCondition, MatchValue
from qdrant_client.models import PointStruct, ScoredPoint
from qdrant_client.models import UpdateStatus


def test_check_install(client, collection, collection_name):
    operation_info = client.upsert(
        collection_name=collection_name,
        wait=True,
        points=[
            PointStruct(id=1, vector=[0.05, 0.61, 0.76, 0.74], payload={"city": "Berlin"}),
            PointStruct(id=2, vector=[0.19, 0.81, 0.75, 0.11], payload={"city": "London"}),
            PointStruct(id=3, vector=[0.36, 0.55, 0.47, 0.94], payload={"city": "Moscow"}),
            PointStruct(id=4, vector=[0.18, 0.01, 0.85, 0.80], payload={"city": "New York"}),
            PointStruct(id=5, vector=[0.24, 0.18, 0.22, 0.44], payload={"city": "Beijing"}),
            PointStruct(id=6, vector=[0.35, 0.08, 0.11, 0.44], payload={"city": "Mumbai"}),
        ],
    )
    assert operation_info.status == UpdateStatus.COMPLETED

    search_result = client.query_points(
        collection_name=collection_name, query=[0.2, 0.1, 0.9, 0.7], with_payload=False, limit=3
    ).points

    assert search_result == [
        ScoredPoint(id=4, version=1, score=1.362, payload=None, vector=None),
        ScoredPoint(id=1, version=1, score=1.273, payload=None, vector=None),
        ScoredPoint(id=3, version=1, score=1.208, payload=None, vector=None),
    ]

    search_result = client.query_points(
        collection_name=collection_name,
        query=[0.2, 0.1, 0.9, 0.7],
        query_filter=Filter(must=[FieldCondition(key="city", match=MatchValue(value="London"))]),
        with_payload=True,
        limit=3,
    ).points

    assert search_result == [
        ScoredPoint(
            id=2, version=1, score=0.871, payload={"city": "London"}, vector=None, shard_key=None, order_value=None
        )
    ]
