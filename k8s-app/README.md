# Kubernetes Database Application Deployment

This repository contains Kubernetes manifests for deploying a database application. Below are the YAML files included and their purposes:

- `mongodb.yaml`: Contains the MongoDB deployment configuration.
- `mongodb_pv.yaml`: Defines the PersistentVolume (PV) configuration for MongoDB data storage.
- `web_app.yaml`: Specifies the deployment configuration for the web application that interacts with MongoDB.

## Prerequisites

Before deploying this application, ensure you have the following installed and configured:

- Kubernetes cluster (minikube, GKE, EKS, etc.)
- `kubectl` command-line tool configured to access your cluster

## Usage

To deploy the remediation module, apply the manifests using `kubectl`:

```bash
kubectl apply -f mongodb.yaml
kubectl apply -f mongodb_pv.yaml
kubectl apply -f web_app.yaml
```

- Verify deployment:
```bash
kubectl get pods  # Check if all pods are running
kubectl get svc   # Retrieve the service endpoints
```
## Accessing the Application
Once deployed, you can access the web application through its service endpoint. Ensure to configure any necessary ingress or load balancer settings depending on your cluster setup.