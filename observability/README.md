# OpenTelemetry Demo Helm Chart

The helm chart installs [OpenTelemetry Demo](https://github.com/open-telemetry/opentelemetry-demo)
in kubernetes cluster.

## Prerequisites

- Kubernetes 1.24+
- Helm 3.9+

## Installing the Chart

Add OpenTelemetry Helm repository:

```console
helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts
```

To install the chart with the release name my-otel-demo with prometheus, alertmanager, persistent volume for prometheus and jaeger run the following command:

```console
helm install my-otel-demo open-telemetry/opentelemetry-demo 
    --set jaeger.enabled=true 
    --set prometheus.alertmanager.enabled=true
    --set prometheus.prometheus-node-exporter.enabled=true
    --set prometheus.kube-state-metrics.enabled=true
    --set prometheus.server.persistentVolume.enabled=true

```

## Official GitHub Repository

- [OpenTelemetry Demo Helm Chart](https://github.com/open-telemetry/opentelemetry-helm-charts)