# Issues

I ran into an issue where `kind` wasn't working.
I kept getting the following error:

```bash
kind get service
The connection to the server localhost:8080 was refused - did you specify the right host or port?
```

I searched online for a resolution, but everyone kept talking about creating an environment variable and creating some admin.config file in my home directory.
All hogwash.

The solution to my problem was to just start over.

```bash
cd
kind delete cluster
Deleting cluster "kind" ...
kind get cluster
ERROR: unknown command "cluster" for "kind get"
mv .kube kube_orig
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
kubectl get service
NAME         TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
kubernetes   ClusterIP   10.96.0.1    <none>        443/TCP   53s
```

Now it's working!
