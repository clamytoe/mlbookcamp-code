from calendar import c
import bentoml

from bentoml.io import JSON


tag = 'credit_risk_model:latest'
model_ref = bentoml.xgboost.get(tag)
dv = model_ref.custom_objects['dictVectorizer']

model_runner = model_ref.to_runner()

svc = bentoml.Service(
    "credit_risk_classifier",
    runners=[model_runner]
)


@svc.api(input=JSON(), output=JSON())
def classify(application_data):
    vector = dv.transform(application_data)
    prediction = model_runner.predict.run(vector)

    print(f'####\n{prediction=}\n####')

    result = prediction[0]

    match result:
        case _ if result > 0.5:
            return { "status": "DECLINED" }
        case _ if result > 0.23:
            return { "status": "MAYBE" }
        case _ :
            return { "status": "APPROVED" }
