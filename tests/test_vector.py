import pytest
from qdrant_client import models


@pytest.mark.parametrize(
    "collection",
    [
        {
            "kwargs": {
                "vectors_config": {
                    "size": 4,
                    "distance": models.Distance.DOT,
                    "multivector_config": models.MultiVectorConfig(comparator=models.MultiVectorComparator.MAX_SIM),
                },
            }
        }
    ],
    indirect=True,
)
async def test_multi_vector(async_client, collection, collection_name):
    multi_vector = [
        [0, 0, 0, 0],
        [
            1,
            2,
            3,
            4,
        ],
        [
            0,
            2,
            2,
            2,
        ],
    ]
    await async_client.upsert(
        collection_name,
        points=[
            models.PointStruct(
                id=1,
                vector=multi_vector,
            )
        ],
    )

    points = await async_client.query_points(
        collection_name,
        query=[
            [0, 0, 0, 0],
            [
                1,
                2,
                3,
                4,
            ],
            [
                0,
                2,
                2,
                2,
            ],
        ],
        with_vectors=True,
    )
    assert points.points[0].vector == multi_vector
