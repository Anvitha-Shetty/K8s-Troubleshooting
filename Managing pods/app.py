from flask import Flask, render_template, request, redirect, url_for
from kubernetes import client, config
import signal
import sys

app = Flask(__name__)


config.load_incluster_config()


v1 = client.CoreV1Api()
namespace = "default"
label_selectors = {
    "app=web": {"cpu": 6, "memory": 85},  
    "app=mongodb": {"cpu": 6, "memory": 70} 
}

def convert_cpu_usage(cpu_usage_str):
    if cpu_usage_str.endswith('n'):
        return float(cpu_usage_str[:-1]) / 1e6
    elif cpu_usage_str.endswith('u'):
        return float(cpu_usage_str[:-1]) / 1e3
    elif cpu_usage_str.endswith('m'):
        return float(cpu_usage_str[:-1])
    else:
        return float(cpu_usage_str) * 1000

def convert_memory_usage(memory_usage_str):
    if memory_usage_str.endswith('Ki'):
        return float(memory_usage_str[:-2]) / 1024
    elif memory_usage_str.endswith('Mi'):
        return float(memory_usage_str[:-2])
    elif memory_usage_str.endswith('Gi'):
        return float(memory_usage_str[:-2]) * 1024
    else:
        return float(memory_usage_str) / (1024 * 1024)

def get_pod_cpu_memory_usage(api_instance, namespace, label_selectors):
    try:
        metrics_api = client.CustomObjectsApi()
        usages = []
        for label_selector, thresholds in label_selectors.items():
            cpu_threshold = thresholds["cpu"]
            memory_threshold = thresholds["memory"]
            pod_metrics_list = metrics_api.list_namespaced_custom_object(
                group="metrics.k8s.io",
                version="v1beta1",
                namespace=namespace,
                plural="pods",
                label_selector=label_selector
            )
            for item in pod_metrics_list['items']:
                containers = item['containers']
                for container in containers:
                    cpu_usage = container['usage']['cpu']
                    cpu_usage_value = convert_cpu_usage(cpu_usage)
                    memory_usage = container['usage']['memory']
                    memory_usage_value = convert_memory_usage(memory_usage)
                    usages.append((item['metadata']['name'], cpu_usage, cpu_usage_value, memory_usage, memory_usage_value, label_selector))
        return usages
    except Exception as e:
        print(f"Error retrieving CPU and memory usage: {e}")
        return []

def restart_pod(api_instance, namespace, pod_name):
    try:
        api_instance.delete_namespaced_pod(pod_name, namespace)
        print(f"Pod {pod_name} restarted successfully.")
    except Exception as e:
        print(f"Error restarting pod {pod_name}: {e}")

@app.route('/')
def index():
    pod_usages = get_pod_cpu_memory_usage(v1, namespace, label_selectors)
    alerts = []
    for pod in pod_usages:
        selector = pod[5] 
        thresholds = label_selectors.get(selector, {})
        if pod[2] > thresholds.get("cpu", float("inf")) or pod[4] > thresholds.get("memory", float("inf")):
            alerts.append(pod)
    return render_template('index.html', pod_usages=pod_usages, alerts=alerts)

@app.route('/restart', methods=['POST'])
def restart():
    pod_name = request.form['pod_name']
    restart_pod(v1, namespace, pod_name)
    return redirect(url_for('index'))

def signal_handler(sig, frame):
    print("Exiting gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    app.run(debug=True)
