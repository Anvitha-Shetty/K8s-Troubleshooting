

# Pod Manager

Pod Manager is a tool for managing pods in a Kubernetes cluster. It provides functionalities to monitor pod metrics and perform pod operations such as deletion.

## Deployment

Before deploying Pod Manager, ensure that the Metrics Server is deployed on the Kubernetes cluster.


### Deploying Pod Manager

Use the following commands to deploy Pod Manager on Kubernetes:

1. Apply Cluster Roles:

```bash
kubectl apply -f cluster_roles.yaml
```

2. Deploy the Pod Manager Deployment:

```bash
kubectl apply -f deployment.yaml
```



3. Deploy the Pod Manager Service:

```bash
kubectl apply -f service.yaml
```


## Usage

Once Pod Manager is deployed, you can access its functionalities through the provided endpoints or interfaces.

