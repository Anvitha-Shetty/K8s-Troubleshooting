# Deployment and Configuration of Student Application

This section encompasses the deployment and configuration procedures for the database application. It includes the configuration files necessary for the persistent volume, MongoDB deployment, and web application deployment.

## Prerequisites

Prior to proceeding with the configuration application, ensure that the following prerequisites are met:

- A running Kubernetes cluster.
- Configuration of the `kubectl` command-line tool to communicate with your cluster.

## Configuration

The file `mongodb_pv.yaml` specifies the attributes of the PersistentVolume (PV), including storage capacity, access modes, and storage class.

Additionally, the files `mongodb.yaml` and `web_app.yaml` contain configurations for MongoDB and web application deployments, respectively.

To apply the configuration, utilize `kubectl` as follows:

```
kubectl apply -f mongodb_pv.yaml
```
```
kubectl apply -f mongodb.yaml
```
```
kubectl apply -f web_app.yaml
```

## Verification

After applying the configuration, you can verify the creation of the PersistentVolume (PV) using the following command:

```bash
kubectl get pv