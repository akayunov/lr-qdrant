import operator
from random import randint

from qdrant_client import models
from qdrant_client.http.models import FacetResponse, FacetValueHit


async def test_facet_collection(async_client, collection_name, collection):
    await async_client.create_payload_index(
        collection_name, field_name="colour", field_schema=models.PayloadSchemaType.KEYWORD
    )

    points = []
    counter = 0
    for colour in (*(["red"]) * 3, *(["blue"] * 3), *(["green"] * 3), "yellow", "x", "y", "z", "a", "b", "c", "d"):
        for k in range(10):
            points.append(
                models.PointStruct(
                    id=counter, vector=[1, 1, 1, randint(0, 1)], payload={"colour": colour, "field2": k}
                ),
            )
            counter += 1
    await async_client.upsert(
        collection_name,
        points=points,
    )
    points = await async_client.facet(
        collection_name,
        key="colour",
        facet_filter=models.Filter(
            must=[models.FieldCondition(key="field2", range=models.Range(gte=0))]  # dummy range
        ),
    )

    assert points == FacetResponse(
        hits=[
            FacetValueHit(value="blue", count=30),
            FacetValueHit(value="green", count=30),
            FacetValueHit(value="red", count=30),
            FacetValueHit(value="a", count=10),
            FacetValueHit(value="b", count=10),
            FacetValueHit(value="c", count=10),
            FacetValueHit(value="d", count=10),
            FacetValueHit(value="x", count=10),
            FacetValueHit(value="y", count=10),
            FacetValueHit(value="yellow", count=10),
        ]
    )  # default limit 10

    points = await async_client.facet(
        collection_name,
        key="colour",
        facet_filter=models.Filter(
            must=[models.FieldCondition(key="field2", range=models.Range(gte=0))]  # dummy range
        ),
        limit=100,
    )

    assert points == FacetResponse(
        hits=[
            FacetValueHit(value="blue", count=30),
            FacetValueHit(value="green", count=30),
            FacetValueHit(value="red", count=30),
            FacetValueHit(value="a", count=10),
            FacetValueHit(value="b", count=10),
            FacetValueHit(value="c", count=10),
            FacetValueHit(value="d", count=10),
            FacetValueHit(value="x", count=10),
            FacetValueHit(value="y", count=10),
            FacetValueHit(value="yellow", count=10),
            FacetValueHit(value="z", count=10),
        ]
    )

    # points = await async_client.facet(
    #     collection_name,
    #     key="colour",
    #     facet_filter=models.Filter(
    #         must=[models.FieldCondition(key="field2", range=models.Range(gte=0))]  # dummy range
    #     ),
    #     exact=True,  # in case exact=False result will be approximate
    # )
    #
    # assert points == FacetResponse(
    #     hits=sorted([
    #         FacetValueHit(value="blue", count=30),
    #         FacetValueHit(value="green", count=30),
    #         FacetValueHit(value="red", count=30),
    #         FacetValueHit(value="a", count=10),
    #         FacetValueHit(value="b", count=10),
    #         FacetValueHit(value="c", count=10),
    #         FacetValueHit(value="d", count=10),
    #         FacetValueHit(value="x", count=10),
    #         FacetValueHit(value="z", count=10),
    #         FacetValueHit(value="y", count=8),  # approximate
    #     ], key=operator.attrgetter('value'))
    # )
