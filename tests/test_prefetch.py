from numpy.ma.core import indices
from openai.resources.admin.organization.users import users
from qdrant_client import models
from qdrant_client.http.models import Record


async def test_filtering(async_client, collection, collection_name):
    points = await async_client.query_points(
        collection_name,
        prefetch=[
            models.Prefetch(
                query=models.SparseVector(indices=[1,2], values=[1,2]),
                using="sparse",
                limit=20,
            ),
            models.Prefetch(
                query=[0.01, 0.02],
                using="dense",
                limit=20
            )
        ],
        query=models.RrfQuery(rrf=models.Rrf())
    )
