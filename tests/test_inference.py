import pytest
from qdrant_client import models
from qdrant_client.http.models import Record, SparseVector, QueryResponse, ScoredPoint


@pytest.mark.parametrize(
    "collection",
    [
        {
            "kwargs": {  # у нас будет разреженный вектор с именем "my-bm25-vector"
                "sparse_vectors_config": {"my-bm25-vector": models.SparseVectorParams()},
                # Так как этот тест только для sparse-векторов, отключаем дефолтный плотный вектор
                "vectors_config": {},
            }
        }
    ],
    indirect=True,
)
async def test_inference(async_client, collection, collection_name):
    await async_client.upsert(
        collection_name,
        points=[
            models.PointStruct(
                id=1,
                vector={
                    "my-bm25-vector": models.Document(
                        text="Recipe for baking chocolate chip cookies",
                        model="Qdrant/bm25",
                    )
                },
            )
        ],
    )

    points = await async_client.retrieve(collection_name, ids=[1], with_vectors=True)
    assert points == [
        Record(
            id=1,
            payload={},
            vector={
                "my-bm25-vector": SparseVector(
                    indices=[112174620, 177304315, 662344706, 771857363, 1617337648],
                    values=[1.6697302, 1.6697302, 1.6697302, 1.6697302, 1.6697302],
                )
            },
            shard_key=None,
            order_value=None,
        )
    ]
    points = await async_client.query_points(
        collection_name=collection_name,
        query=models.Document(
            text="How to bake cookies?",
            model="Qdrant/bm25",
        ),
        using="my-bm25-vector",
        with_vectors=True,
    )
    assert points == QueryResponse(
        points=[
            ScoredPoint(
                id=1,
                version=1,
                score=3.3394604,
                payload={},
                vector={
                    "my-bm25-vector": SparseVector(
                        indices=[112174620, 177304315, 662344706, 771857363, 1617337648],
                        values=[1.6697302, 1.6697302, 1.6697302, 1.6697302, 1.6697302],
                    )
                },
                shard_key=None,
                order_value=None,
            )
        ]
    )
