from qdrant_client.http.models import models, PayloadIndexInfo, PayloadSchemaType


async def test_payload_index(async_client, collection, collection_name):
    await async_client.create_payload_index(
        collection_name, field_name="some_name", field_schema=models.PayloadSchemaType.KEYWORD
    )
    coll_info = await async_client.get_collection(collection_name=collection_name)
    assert coll_info.payload_schema == {
        "some_name": PayloadIndexInfo(data_type=PayloadSchemaType.KEYWORD, params=None, points=0)
    }
