# Remediation Module for Kubernetes Cluster

This repository contains Kubernetes manifests to set up a remediation module for handling node issues automatically in a Kubernetes cluster.

## Manifests

- **deployment.yaml**: Contains the deployment configuration for the remediation service.
- **role.yaml**: Defines the Kubernetes RBAC role required for the remediation service.
- **rolebinding.yaml**: Specifies the role binding to associate the role with the service account.
- **service.yaml**: Defines the Kubernetes service for accessing the remediation service.

## Usage

To deploy the remediation module, apply the manifests using `kubectl`:

```bash
kubectl apply -f deployment.yaml
kubectl apply -f role.yaml
kubectl apply -f rolebinding.yaml
kubectl apply -f service.yaml
