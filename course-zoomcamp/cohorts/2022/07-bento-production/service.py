import bentoml
import numpy as np
from bentoml.io import JSON, NumpyNdarray
from pydantic import BaseModel


class UserProfile(BaseModel):
    name: str
    age: int
    country: str
    rating: float


# tag = "mlzoomcamp_homework:qtzdz3slg6mwwdu5"
tag = "mlzoomcamp_homework:jsi67fslz6txydu5"
model_ref = bentoml.sklearn.get(tag)
model_runner = model_ref.to_runner()

svc = bentoml.Service("user_profile_classifier", runners=[model_runner])


@svc.api(
    input=NumpyNdarray(),
    output=NumpyNdarray()
)
async def classify(user_profile):
    prediction = await model_runner.predict.async_run(user_profile)

    print(f"####\n{prediction=}\n####")

    return prediction
