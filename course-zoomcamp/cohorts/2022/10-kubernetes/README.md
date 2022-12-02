# Week 10 Issues

## Connection refused

I ran into an issue where `kubectl` wasn't working.
I kept getting the following error:

```bash
kubectl get service
The connection to the server localhost:8080 was refused - did you specify the right host or port?
```

I searched online for a resolution, but everyone kept talking about creating an environment variable and creating some admin.config file in my home directory.
All hogwash.

The solution to my problem was to just start over.

```bash
cd
kind delete cluster
Deleting cluster "kind" ...
rm -rf .kube
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

Not sure what to do next? 😅  Check out https://kind.sigs.k8s.io/docs/user/quick-start/
kubectl cluster-info --context kind-kind
Kubernetes control plane is running at https://127.0.0.1:41651
CoreDNS is running at https://127.0.0.1:41651/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
```

Now when I try the same command again:

```
kubectl get service
NAME         TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
kubernetes   ClusterIP   10.96.0.1    <none>        443/TCP   53s
```

Now it's working!

## HPA not updating

Another issue that I had was that HPA was not updating.
I attempted the fix that Alexey had provided:

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

But it was still not updating. Perhaps it was because I didn't stop/start the portforwarding... not sure.
At any rate, I found a post by Marilina Orihuela with a solution that did work:

```bash
kubectl edit deploy -n kube-system metrics-server
```

From the `vi` session that opens, type: `/--kubelet` and hit Enter.
Then click on the `n` key until you get to a section that resembles this:

```yaml
  template:
    metadata:
      creationTimestamp: null
      labels:
        k8s-app: metrics-server
    spec:
      containers:
      - args:
        - --cert-dir=/tmp
        - --secure-port=4443
        - --kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname
        - --kubelet-use-node-status-port
        - --metric-resolution=15s
        image: k8s.gcr.io/metrics-server/metrics-server:v0.6.2
```

Add `- --kubelet-insecure-tls` in the args section right after the secure-port argument:

```yaml


```yaml
  template:
    metadata:
      creationTimestamp: null
      labels:
        k8s-app: metrics-server
    spec:
      containers:
      - args:
        - --cert-dir=/tmp
        - --secure-port=4443
        - --kubelet-insecure-tls
        - --kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname
        - --kubelet-use-node-status-port
        - --metric-resolution=15s
        image: k8s.gcr.io/metrics-server/metrics-server:v0.6.2
```

Now initially it didn't appear to have worked, until I stopped the port forwarding and the looping script.
After starting it back up, the `kubectl get hpa` was updating its values!
