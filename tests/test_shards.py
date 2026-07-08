import pytest
from qdrant_client.conversions.common_types import CollectionClusterInfo
from qdrant_client.models import Filter, FieldCondition, MatchValue
from qdrant_client.models import PointStruct, ScoredPoint
from qdrant_client.models import UpdateStatus


@pytest.mark.parametrize(
    "collection",  # параметры для фикстуры collection
    [{"kwargs": {"shard_number": 1, "sharding_method": "custom"}}],  # сколько шард на один ключ  # свое шардирование
    indirect=True,
)
def test_check_install(client, collection, collection_name):
    client.create_shard_key(
        collection_name=collection_name,
        shard_key="shard_key_1",
    )
    operation_info = client.upsert(
        collection_name=collection_name,
        wait=True,
        points=[
            PointStruct(id=1, vector=[0.05, 0.61, 0.76, 0.74], payload={"city": "Berlin"}),
        ],
        shard_key_selector="shard_key_1",
    )
    assert operation_info.status == UpdateStatus.COMPLETED

    search_result = client.query_points(
        collection_name=collection_name, query=[0.05, 0.61, 0.76, 0.74], with_payload=True, limit=3
    ).points

    client.create_shard_key(
        collection_name=collection_name,
        shard_key="shard_key_2",  # will lead to second shard creation
    )
    operation_info = client.upsert(
        collection_name=collection_name,
        wait=True,
        points=[
            PointStruct(id=1, vector=[0.35, 0.08, 0.11, 0.44], payload={"city": "Berlin"}),
        ],
        shard_key_selector="shard_key_2",
    )
    assert operation_info.status == UpdateStatus.COMPLETED

    c_info = client.collection_cluster_info(
        collection_name=collection_name,
    )
    assert c_info.shard_count == 2
    assert c_info.shard_count == 2
