# Project Overview

This project focuses on troubleshooting and enhancing the debuggability of Kubernetes clusters and application performance. It integrates several key tools and components to monitor, trace, and manage Kubernetes resources effectively.

## Kubernetes Database Application

### Overview

This part of the project involves developing and deploying a database application on Kubernetes. The application utilizes MongoDB for data storage, with separate pods for the web application frontend and MongoDB backend.

### Features

- **Database Operations**: Basic CRUD operations (Create, Read, Update, Delete) are implemented for managing student records.
- **Error Handling**: Error paths are implemented for each function, with logs, metrics, and traces collected to facilitate debugging and monitoring.

## Observability and Monitoring

### Overview

The observability stack integrates metrics collection, distributed tracing, and log management to provide insights into the Kubernetes environment and application performance.

### Components

- **Metrics Collection**: OpenTelemetry collects metrics such as CPU, memory, and network usage from Kubernetes pods and nodes. These metrics are stored and queried using Prometheus.
- **Distributed Tracing**: OpenTelemetry captures traces across microservices deployed in Kubernetes, providing visibility into request flows and latency. Jaeger serves as the backend for storage, visualization, and analysis of trace data
- **Log Management**: Logs from Kubernetes pods are also collected.

### Visualization

- **Grafana Dashboards**: Grafana is used to visualize metrics from Prometheus and traces from Jaeger. Custom dashboards monitor resource usage, application performance metrics. Dashboard for Node exporter is used for hardware and operating system metrics.

### Example Application Monitoring

The Kubernetes database application developed in Part 1 serves as an example for monitoring and visualizing database metrics in Grafana.

## Remediation Module

### Overview

The remediation module focuses on automating the detection and resolution of core node-level issues within the Kubernetes cluster.

### Integration

- **Node Problem Detector**: Integrated with the remediation system to detect kernel-level problems and other node health issues.
- **Metrics Server**: Monitors CPU and memory usage, triggering alerts and automated actions when thresholds are exceeded.
- **Remediation Actions**: Automated actions include pod restarts, resource limit adjustments, and dynamic scaling of application replicas based on predefined thresholds.

### Example Scenario

Simulated scenarios using tools like stress-ng trigger alerts in the Kubernetes cluster. The remediation module responds by executing automated actions to maintain cluster health and application performance.

