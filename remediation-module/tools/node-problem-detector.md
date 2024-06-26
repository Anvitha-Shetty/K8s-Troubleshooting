## Node Problem Detector

The Node Problem Detector is a Kubernetes component that detects node-level problems, such as hardware failures or kernel panics, and triggers corresponding Kubernetes events or actions for remediation.

Node-problem-detector aims to make various node problems visible to the upstream
layers in the cluster management stack.
It is a daemon that runs on each node, detects node
problems and reports them to apiserver.
node-problem-detector can either run as a
[DaemonSet](https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/) or run standalone.
Now it is running as a
[Kubernetes Addon](https://github.com/kubernetes/kubernetes/tree/master/cluster/addons)
enabled by default in the GKE cluster. It is also enabled by default in AKS as part of the
[AKS Linux Extension](https://learn.microsoft.com/en-us/azure/aks/faq#what-is-the-purpose-of-the-aks-linux-extension-i-see-installed-on-my-linux-vmss-instances).
# Background

There are tons of node problems that could possibly affect the pods running on the
node, such as:
* Infrastructure daemon issues: ntp service down;
* Hardware issues: Bad CPU, memory or disk;
* Kernel issues: Kernel deadlock, corrupted file system;
* Container runtime issues: Unresponsive runtime daemon;
* ...

Currently, these problems are invisible to the upstream layers in the cluster management
stack, so Kubernetes will continue scheduling pods to the bad nodes.

To solve this problem, we introduced this new daemon **node-problem-detector** to
collect node problems from various daemons and make them visible to the upstream
layers. Once upstream layers have visibility to those problems, we can discuss the
[remedy system](#remedy-systems).

## Official GitHub Repository
- [Node Problem Detector Documentation](https://github.com/kubernetes/node-problem-detector)




