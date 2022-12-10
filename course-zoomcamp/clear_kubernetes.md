# Clean up commands for kubectl and kind

## stop all kubectl services

```bash
kubectl get services
kubectl delete svc credit-card
kubectl delete svc kubernetes
```

## delete the kind cluster

```bash
kind delete cluster
```

## delete the docker image

```bash
docker images
docker rmi kindest/node
```
