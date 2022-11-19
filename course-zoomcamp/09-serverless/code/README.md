# Docker commands

## To build image

```bash
docker build -t clothing-model .
```

## To run image

```bash
docker run -it --rm -p 8080:8080 clothing-model:latest
```

## Compiled versions of tflite

[Tensorflow:latest](https://github.com/tensorflow/tensorflow/releases)
[tflite-aws-lambda](https://github.com/alexeygrigorev/tflite-aws-lambda)

## Tensorflow repo

[repo](https://github.com/tensorflow/tensorflow.git)

## AWS Elastic Container Registry

```aws
aws ecr create-repository --repository-name clothing-tflite-images

{
    "repository": {
        "repositoryArn": "arn:aws:ecr:us-east-1:<ACCOUNT_NUMBER>:repository/clothing-tflite-images",
        "registryId": "<ACCOUNT_NUMBER>",
        "repositoryName": "clothing-tflite-images",
        "repositoryUri": "<ACCOUNT_NUMBER>.dkr.ecr.us-east-1.amazonaws.com/clothing-tflite-images",
        "createdAt": "2022-11-18T20:15:45-06:00",
        "imageTagMutability": "MUTABLE",
        "imageScanningConfiguration": {
            "scanOnPush": false
        },
        "encryptionConfiguration": {
            "encryptionType": "AES256"
        }
    }
}
```

### Get login

```aws
aws ecr get-login-password
```

### Log in to AWS

```aws
docker login -u AWS -p $PASSWORD <ACCOUNT_NUMBER>.dkr.ecr.us-east-1.amazonaws.com/clothing-tflite-images
```

### Construct URI

```bash
ACCOUNT=<ACCOUNT_NUMBER>
REGION=us-east-1
REGISTRY=clothing-tflite-images
PREFIX=${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com/${REGISTRY}

TAG=clothing-model-xception-v4-001
REMOTE_URI=${PREFIX}:${TAG}
```

Confirm that it worked:

```bash
echo $REMOTE_URI
<ACCOUNT_NUMBER>.dkr.ecr.us-east-1.amazonaws.com/clothing-tflite-images:clothing-model-xception-v4-001
```

### Tag and push the docker image

```docker
docker tag clothing-model:latest ${REMOTE_URI}
docker push ${REMOTE_URI}
```

## AWS Lambda

1. Create a new function from an image.
2. Select the newly uploaded image.
3. Create a test for it.
4. From Configuration, give it:
    * 1024MB of memory
    * 30 seconds timeout

## Creating an API Gateway

1. Go to API Gateway
2. Build from REST API
    * with API management capabilities
3. Select New API
4. Give it a name
5. Click Create API
6. From Actions, select Create Resource
    * Name it: predict
    * Click on Create Resource
7. From Actions, select Create Method
    * from drop-down list select POST
    * click on the check mark
    * From POST - Setup
        * select Lambda Function
        * give it a name
        * click on Save
    * At the prompt allow the permission change
        > You are about to give API Gateway permission to invoke your Lambda function:
arn:aws:lambda:us-east-1:<ACCOUNT_NUMBER>:function:clothing-classification
8. Click on Test
9. Move down to Request Body
    * Enter:
        * {"url": "http://bit.ly/mlbookcamp-pants"}
    * Click on the Test button
10. Click on Actions again, and select Deploy API
    * Select New Stage
    * Stage name: test
    * Click on Deploy button
11. You should have an test url now:
    * [https://<URL_ID>.execute-api.us-east-1.amazonaws.com/test](https://<URL_ID>.execute-api.us-east-1.amazonaws.com/test)
12. Modify url in your test script and test it
