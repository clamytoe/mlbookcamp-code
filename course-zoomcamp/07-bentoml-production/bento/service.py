import bentoml
from bentoml.io import JSON
from pydantic import BaseModel


class CreditApplication(BaseModel):
    seniority: int
    home: str
    time: int
    age: int
    marital: str
    records: str
    job: str
    expenses: int
    income: float
    assets: float
    debt: float
    amount: int
    price: int


# tag = "credit_risk_model:latest"
tag = 'credit_risk_model:mt7zuukplobymdg5'
model_ref = bentoml.xgboost.get(tag)
dv = model_ref.custom_objects["dictVectorizer"]

model_runner = model_ref.to_runner()

svc = bentoml.Service("credit_risk_classifier", runners=[model_runner])


@svc.api(input=JSON(), output=JSON())
async def classify(application_data: CreditApplication):
    vector = dv.transform(application_data)
    prediction = await model_runner.predict.async_run(vector)

    print(f"####\n{prediction=}\n####")

    result = prediction[0]

    if result > 0.5:
        return {"status": "DECLINED"}
    elif result > 0.23:
        return {"status": "MAYBE"}
    else:
        return {"status": "APPROVED"}
