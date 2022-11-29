# Kubernetes

## Convert tensorflow model to saved model format

```bash
model_file = 'clothing-model.h5'
ipython
In [1]: import tensorflow as tf
In [2]: from tensorflow import keras
In [3]: model = keras.models.load_model('./clothing-model.h5')
In [4]: model
Out[4]: <keras.engine.functional.Functional at 0x7f8a31d10be0>
In [5]: tf.saved_model.save(model, 'clothing-model')
```

> **NOTE:** `clothing-model` here is the directory where the model will be saved.

## To view the saved model

Keras has a command line utility called `saved_model_cli` that can be used:

```keras
saved_model_cli show --dir clothing-model --all
MetaGraphDef with tag-set: 'serve' contains the following SignatureDefs:

...
signature_def['serving_default']:
  The given SavedModel SignatureDef contains the following input(s):
    inputs['input_8'] tensor_info:
        dtype: DT_FLOAT
        shape: (-1, 299, 299, 3)
        name: serving_default_input_8:0
  The given SavedModel SignatureDef contains the following output(s):
    outputs['dense_7'] tensor_info:
        dtype: DT_FLOAT
        shape: (-1, 10)
        name: StatefulPartitionedCall:0
  Method name is: tensorflow/serving/predict
...
```

> We're mostly interested in the signature defenition.

## Create docker image

We now contruct our docker image with the following settings:

* expose port 8500
* create a volume of the model directory
* create environment variable for the model name
* specify the image to use

```docker
docker run -it --rm \
  -p 8500:8500 \
  -v "${PWD}/clothing-model:/models/clothing-model/1" \
  -e MODEL_NAME="clothing-model" \
  tensorflow/serving:2.7.0
```

## Use the service

Full instructions and code are availabel in tf-serving-connect.ipynb

## Package incompatabilities with protobuf

Run the following command to fix:

```bash
pip install --upgrade "protobuf<=3.19.1" "grpcio<=1.42.0" "grpcio-tools<=1.42.0"
pipenv install tensorflow-protobuf==2.11.0
```

## Create pipenv virtual environment

```bash
pipenv install grpcio==1.42.0 flask gunicorn keras-image-helper
```

## Create our custom docker images

### Model

Let's start by creating a Dockerfile for our model:

*image-model.dockerfile:*

```docker
FROM tensorflow/serving:2.7.0

COPY clothing-model /models/clothing-model/1
ENV MODEL_NAME="clothing-model"
```

Then build our image:

```docker
docker build \
  -t zoomcamp-10-model:xception-v4-001 \
  -f image-model.dockerfile \
  .
```

Run it:

```docker
docker run -it --rm \
  -p 8500:8500 \
  zoomcamp-10-model:xception-v4-001
``

Test it:

```bash
pipenv run python gateway.py
{'dress': -1.87986421585083, 'hat': -4.75631046295166, 'longsleeve': -2.359531879425049, 'outwear': -1.08926522731781, 'pants': 9.903782844543457, 'shirt': -2.826179027557373, 'shoes': -3.648310422897339, 'shorts': 3.241154909133911, 'skirt': -2.612096071243286, 't-shirt': -4.852035045623779}
```

### Flask app

Now to create the dockerfile for our flask app:

*image-gateway.dockerfile:*

```docker
FROM python:3.9-slim

RUN pip install pipenv

WORKDIR /app

COPY ["Pipfile", "Pipfile.lock", "./"]

RUN pipenv install --system --deploy

COPY ["gateway.py", "proto.py", "./"]

EXPOSE 9696

ENTRYPOINT ["gunicorn", "--bind=0.0.0.0:9696", "gateway:app"]
```

Build it:

```docker
docker build \
  -t zoomcamp-10-gateway:001 \
  -f image-gateway.dockerfile \
  .
```

Run it:

```docker
docker run -it --rm \
  -p 9696:9696 \
  zoomcamp-10-gateway:001
``

Test it:

```bash
python test.py
Traceback (most recent call last):
  File "/home/clamytoe/miniconda3/envs/py39/lib/python3.9/site-packages/requests/models.py", line 971, in json
    return complexjson.loads(self.text, **kwargs)
  File "/home/clamytoe/miniconda3/envs/py39/lib/python3.9/json/__init__.py", line 346, in loads
    return _default_decoder.decode(s)
  File "/home/clamytoe/miniconda3/envs/py39/lib/python3.9/json/decoder.py", line 337, in decode
    obj, end = self.raw_decode(s, idx=_w(s, 0).end())
  File "/home/clamytoe/miniconda3/envs/py39/lib/python3.9/json/decoder.py", line 355, in raw_decode
    raise JSONDecodeError("Expecting value", s, err.value) from None
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/mnt/c/Users/clamy/Projects/mlbookcamp-code/course-zoomcamp/10-kubernetes/code/test.py", line 7, in <module>
    result = requests.post(url, json=data).json()
  File "/home/clamytoe/miniconda3/envs/py39/lib/python3.9/site-packages/requests/models.py", line 975, in json
    raise RequestsJSONDecodeError(e.msg, e.doc, e.pos)
requests.exceptions.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

What happened? The two containers can't communicate with each other.
Let's resolve this next.

## Docker Compose

### Install Docker Compose

```bash
cd
mkdir bin
cd bin/
wget https://github.com/docker/compose/releases/download/v2.13.0/docker-compose-linux-x86_64 -o docker-compose
chmod +x docker-compose
```

> Add the bin directory to your path by adding this line to the end of your .bashrc file: `export PATH="${HOME}/bin:${PATH}"` followed by `source .bashrc` to reload the shell.

### docker-compose.yaml

*docker-compose.yaml:*

```
version: "3.9"
services:
  clothing-model:
    image: zoomcamp-10-model:xception-v4-001
  gateway:
    image: zoomcamp-10-gateway:001
    environment:
      - TF_SERVING_HOST=clothing-model:8500
    ports:
      - "9696:9696"
```

### Starting the services

From the project directory, run the following command:

```bash
docker-compose up
```

Test it:

```bash
python test.py
```

> **NOTE:** To get your terminal back, use the `-d` flag: `docker-compose up -d`

### Stopping the services

```bash
docker-compose down
```

## Introduction to Kubernetes

* **node**: server/container/ec2 instance
* **pod**: docker container, runs on a node
* **deployment**: group of pods with the same image & config
* **service**: entry points to deployments, routes requests to pods
  * **external**: load balancer
  * **internal**: cluster IP
* **ingress**: client facing entry point to cluster
* **HPA**: Horizontal Pod Autoscaler allocates more resources to deployment if it needs them

## Deploy simple service to Kubernetes

Create simple ping application.

1. `mkdir ping; cd $_`
2. `touch Pipfile`
3. `pipenv install flask gunicorn`
4. Create application files:

*ping.py:*

```python
from flask import Flask

app = Flask('ping')

@app.route('/ping', methods=['GET'])
def ping():
    return "PONG"

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9696)
```

*Dockerfile:*

```docker
FROM python:3.9.15-slim

RUN pip install pipenv

WORKDIR /app

COPY ["Pipfile", "Pipfile.lock", "./"]

RUN pipenv install --system --deploy

COPY "ping.py" .

EXPOSE 9696

ENTRYPOINT ["gunicorn", "--bind=0.0.0.0:9696", "ping:app"]
```

5. `docker build -t ping:v001`
6. `docker run -it --rm -p 9696:9696 ping:v001`

Test from another terminal:

```bash
curl localhost:9696/ping
PONG%
```

### Install kubectl

Since we're going to be deploying on AWS, might as well install kubectl from Amazon: [https://docs.aws.amazon.com/eks/latest/userguide/install-kubectl.html](https://docs.aws.amazon.com/eks/latest/userguide/install-kubectl.html)

```bash
cd ~/bin
curl -o kubectl https://s3.us-west-2.amazonaws.com/amazon-eks/1.24.7/2022-10-31/bin/linux/amd64/kubectl
chmod +x kubectl
```

### Install kind

kind: [https://kind.sigs.k8s.io/docs/user/quick-start/#installation](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)

```bash
cd ~/bin
wget -c https://kind.sigs.k8s.io/dl/v0.17.0/kind-linux-amd64 -O kind
chmod +x kind
```

### Create cluster

```bash
kind create cluster
Creating cluster "kind" ...
 ✓ Ensuring node image (kindest/node:v1.25.3) 🖼
 ✓ Preparing nodes 📦
 ✓ Writing configuration 📜
 ✓ Starting control-plane 🕹️
 ✓ Installing CNI 🔌
 ✓ Installing StorageClass 💾
Set kubectl context to "kind-kind"
You can now use your cluster with:

kubectl cluster-info --context kind-kind

Thanks for using kind! 😊
```

See details:

```bash
kubectl cluster-info --context kind-kind
Kubernetes control plane is running at https://127.0.0.1:44153
CoreDNS is running at https://127.0.0.1:44153/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
```

To view all of the services that are running in our cluster:

```bash
kubectl get service
NAME         TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
kubernetes   ClusterIP   10.96.0.1    <none>        443/TCP   5m46s
```

To view pods:

```bash
kubectl get pod
No resources found in default namespace.
```

To view deployments:

```bash
kubectl get deployment
No resources found in default namespace.
```

Can also use:

```docker
docker ps
CONTAINER ID   IMAGE                  COMMAND                  CREATED         STATUS         PORTS
  NAMES
7dbe1bba4193   kindest/node:v1.25.3   "/usr/local/bin/entr…"   9 minutes ago   Up 9 minutes   127.0.0.1:44153->6443/tcp   kind-control-plane
```

### Create a deployment

It is recommended to install the Kubernetes extension from Microsoft for VSCode.
With the extension, simply type `deployment`and a pop-up will show up, click it and it will create the following file structure, ready for you to fill it in:

*deployment.yaml:*

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ping-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ping
  template:
    metadata:
      labels:
        app: ping
    spec:
      containers:
      - name: ping-pod
        image: ping:v001
        resources:
          limits:
            memory: "128Mi"
            cpu: "200m"
        ports:
        - containerPort: 9696
```

To use our `deployment.yaml`:

```bash
kubectl apply -f deployment.yaml
deployment.apps/ping-deployment created
```

To confirm:

```bash
kubectl get deployment
NAME              READY   UP-TO-DATE   AVAILABLE   AGE
ping-deployment   0/1     1            0           36s
```

Check the pod:

```bash
kubectl get pod
NAME                               READY   STATUS             RESTARTS   AGE
ping-deployment-7459f4b7c7-zrjlx   0/1     ImagePullBackOff   0          2m35s
```

Let's see what's wrong with the pod:

```bash
kubectl describe pod ping-deployment-7459f4b7c7-zrjlx
Name:             ping-deployment-7459f4b7c7-zrjlx
Namespace:        default
Priority:         0
Service Account:  default
Node:             kind-control-plane/172.21.0.2
Start Time:       Mon, 28 Nov 2022 21:32:28 -0600
Labels:           app=ping
                  pod-template-hash=7459f4b7c7
Annotations:      <none>
Status:           Pending
IP:               10.244.0.5
IPs:
  IP:           10.244.0.5
Controlled By:  ReplicaSet/ping-deployment-7459f4b7c7
Containers:
  ping-pod:
    Container ID:
    Image:          ping:v001
    Image ID:
    Port:           9696/TCP
    Host Port:      0/TCP
    State:          Waiting
      Reason:       ImagePullBackOff
    Ready:          False
    Restart Count:  0
    Limits:
      cpu:     200m
      memory:  128Mi
    Requests:
      cpu:        200m
      memory:     128Mi
    Environment:  <none>
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from kube-api-access-7t6lh (ro)
Conditions:
  Type              Status
  Initialized       True
  Ready             False
  ContainersReady   False
  PodScheduled      True
Volumes:
  kube-api-access-7t6lh:
    Type:                    Projected (a volume that contains injected data from multiple sources)
    TokenExpirationSeconds:  3607
    ConfigMapName:           kube-root-ca.crt
    ConfigMapOptional:       <nil>
    DownwardAPI:             true
QoS Class:                   Guaranteed
Node-Selectors:              <none>
Tolerations:                 node.kubernetes.io/not-ready:NoExecute op=Exists for 300s
                             node.kubernetes.io/unreachable:NoExecute op=Exists for 300s
Events:
  Type     Reason     Age                    From               Message
  ----     ------     ----                   ----               -------
  Normal   Scheduled  4m19s                  default-scheduler  Successfully assigned default/ping-deployment-7459f4b7c7-zrjlx to kind-control-plane
  Normal   Pulling    2m46s (x4 over 4m19s)  kubelet            Pulling image "ping:v001"
  Warning  Failed     2m46s (x4 over 4m18s)  kubelet            Failed to pull image "ping:v001": rpc error: code = Unknown desc = failed to pull and unpack image "docker.io/library/ping:v001": failed to resolve reference "docker.io/library/ping:v001": pull access denied, repository does not exist or may require authorization: server message: insufficient_scope: authorization failed
  Warning  Failed     2m46s (x4 over 4m18s)  kubelet            Error: ErrImagePull
  Warning  Failed     2m34s (x6 over 4m18s)  kubelet            Error: ImagePullBackOff
  Normal   BackOff    2m21s (x7 over 4m18s)  kubelet            Back-off pulling image "ping:v001"
```

So it wasn't able to pull the image. Let's load the image with `kind`.

```bash
kind load docker-image ping:v001
Image: "" with ID "sha256:dea78965b2136d6f50c733b38466b2433e91ab4cd55eda69761d45ad7b37f7e0" not yet present on node "kind-control-plane", loading...
```

Check the pod once again:

```bash
kubectl get pod
NAME                               READY   STATUS    RESTARTS   AGE
ping-deployment-7459f4b7c7-zrjlx   1/1     Running   0          10m
```

#### Test the deployment

We will use port forwarding to test our deployment

```bash
kubectl port-forward ping-deployment-7459f4b7c7-zrjlx 9696:9696
Forwarding from 127.0.0.1:9696 -> 9696
Forwarding from [::1]:9696 -> 9696
```

From another terminal:

```bash
curl localhost:9696/ping
PONG%
```

On our port-forwarding terminal we should see:

```bash
Handling connection for 9696
```

### Create a service

*service.yaml:*

```yaml
apiVersion: v1
kind: Service
metadata:
  name: ping
spec:
  type: LoadBalancer
  selector:
    app: ping
  ports:
  - port: 80
    targetPort: 9696

```

To create the service:

```bash
kubectl apply -f service.yaml
service/ping created
```

To confirm:

```bash
kubectl get service
NAME         TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
kubernetes   ClusterIP      10.96.0.1      <none>        443/TCP        45m
ping         LoadBalancer   10.96.65.155   <pending>     80:31287/TCP   37s
```

**NOTE:** `kubectl get svc` is a shortcut

#### Test the service

Since we don't have an external IP address, we'll pretend with port-forwarding.

```bash
kubectl port-forward service/ping 8080:80
Forwarding from 127.0.0.1:8080 -> 9696
Forwarding from [::1]:8080 -> 9696
```

From a second terminal:

```bash
curl localhost:8080/ping
PONG%
```

You will see `Handling connection for 8080` on the port-fowarding terminal.

## Sample code

```bash
saved_model_cli

docker run -it --rm \
  -p 8500:8500 \
  -v $(pwd)/clothing-model:/models/clothing-model/1 \
  -e MODEL_NAME="clothing-model" \
  tensorflow/serving:2.7.0


docker build -t zoomcamp-10-model:xception-v4-001 \
  -f image-model.dockerfile .

docker run -it --rm \
  -p 8500:8500 \
  zoomcamp-10-model:xception-v4-001

docker build -t zoomcamp-10-gateway:002 \
  -f image-gateway.dockerfile .

docker run -it --rm \
  -p 9696:9696 \
  zoomcamp-10-gateway:001


docker-compose up

docker-compose up -d
docker-compose down

docker build -t ping:v001 .
docker run -it --rm -p 9696:9696 ping:v001


kind create cluster

kubectl get service
kubectl get pod
kubectl get deployment

kubectl apply -f deployment.yaml

kind load docker-image ping:v001
kubectl port-forward ping-deployment-7df687f8cd-tfkgd 9696:9696

kubectl apply -f service.yaml
kubectl port-forward service/ping 8080:80

kind load docker-image zoomcamp-10-model:xception-v4-001

kubectl port-forward tf-serving-clothing-model-85cd4b7fc9-rntfw 8500:8500

kubectl port-forward service/tf-serving-clothing-model 8500:8500

kind load docker-image zoomcamp-10-gateway:002

kubectl exec -it ping-deployment-577d56ccf5-p2bdq -- bash

apt update
apt install curl telnet 
telnet tf-serving-clothing-model.default.svc.cluster.local 8500

kubectl port-forward service/gateway 8080:80


ACCOUNT_ID=387546586013
REGION=eu-west-1
REGISTRY_NAME=mlzoomcamp-images
PREFIX=${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${REGISTRY_NAME}

GATEWAY_LOCAL=zoomcamp-10-gateway:002
GATEWAY_REMOTE=${PREFIX}:zoomcamp-10-gateway-002
docker tag ${GATEWAY_LOCAL} ${GATEWAY_REMOTE}

MODEL_LOCAL=zoomcamp-10-model:xception-v4-001
MODEL_REMOTE=${PREFIX}:zoomcamp-10-model-xception-v4-001
docker tag ${MODEL_LOCAL} ${MODEL_REMOTE}

docker push ${MODEL_REMOTE}
docker push ${GATEWAY_REMOTE}


eksctl create cluster -f eks-config.yaml
eksctl delete cluster --name mlzoomcamp-eks
```
