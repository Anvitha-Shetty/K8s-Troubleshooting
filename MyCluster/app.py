from flask import Flask, render_template, redirect, url_for, request
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import signal
import paramiko
from flask import jsonify
import subprocess
import sys

app = Flask(__name__)

config.load_kube_config()

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

def restart_pod_manager(api_instance, namespace, pod_name):
    try:
        api_instance.delete_namespaced_pod(pod_name, namespace)
        print(f"Pod {pod_name} restarted successfully.")
    except Exception as e:
        print(f"Error restarting pod {pod_name}: {e}")

##
def get_node_metrics():
    try:
        output = subprocess.check_output(["kubectl", "top", "nodes"]).decode('utf-8')
        lines = output.split('\n')[1:] 
        node_metrics = []

        for line in lines:
            if not line:
                continue
            parts = line.split()
            node_name = parts[0]
            cpu_usage = parts[1]
            cpu_percent = parts[2]
            memory_usage = parts[3]
            memory_percent = parts[4]
            node_metrics.append({
                "node_name": node_name,
                "cpu_usage": f"{cpu_usage} ({cpu_percent})",
                "memory_usage": f"{memory_usage} ({memory_percent})"
            })

        return node_metrics
    except subprocess.CalledProcessError as e:
        print(f"Error running kubectl top nodes: {e}")
        return []
##

def get_pod_metrics():
    try:
        api_instance = client.CustomObjectsApi()
        group = 'metrics.k8s.io'
        version = 'v1beta1'
        namespace = 'default'
        plural = 'pods'
        metrics = api_instance.list_namespaced_custom_object(group, version, namespace, plural)
        pod_metrics = []

        for item in metrics['items']:
            pod_name = item['metadata']['name']
            cpu_usage = item['containers'][0]['usage']['cpu']
            memory_usage = item['containers'][0]['usage']['memory']
            pod_metrics.append({
                "pod_name": pod_name,
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage
            })

        return pod_metrics
    except ApiException as e:
        print(f"Exception when calling CustomObjectsApi->list_namespaced_custom_object: {e}")
        return []

def get_deployments():
    try:
        api_instance = client.AppsV1Api()
        deployments = api_instance.list_deployment_for_all_namespaces()
        deployment_list = []

        for item in deployments.items:
            deployment_list.append({
                "namespace": item.metadata.namespace,
                "name": item.metadata.name,
                "replicas": item.spec.replicas,
                "available_replicas": item.status.available_replicas
            })

        return deployment_list
    except ApiException as e:
        print(f"Exception when calling AppsV1Api->list_deployment_for_all_namespaces: {e}")
        return []

def get_services():
    try:
        api_instance = client.CoreV1Api()
        services = api_instance.list_service_for_all_namespaces()
        service_list = []

        for item in services.items:
            ports = []
            for port in item.spec.ports:
                ports.append({
                    "port": port.port,
                    "protocol": port.protocol,
                    "target_port": port.target_port,
                    "node_port": port.node_port if hasattr(port, "node_port") else None  # Check if nodePort is defined
                })

            service_list.append({
                "namespace": item.metadata.namespace,
                "name": item.metadata.name,
                "type": item.spec.type,
                "cluster_ip": item.spec.cluster_ip,
                "ports": ports
            })

        return service_list
    except ApiException as e:
        print(f"Exception when calling CoreV1Api->list_service_for_all_namespaces: {e}")
        return []


def get_namespaces():
    try:
        api_instance = client.CoreV1Api()
        namespaces = api_instance.list_namespace()
        namespace_list = []

        for item in namespaces.items:
            namespace_list.append({
                "name": item.metadata.name,
                "status": item.status.phase
            })

        return namespace_list
    except ApiException as e:
        print(f"Exception when calling CoreV1Api->list_namespace: {e}")
        return []

##  
def get_node_conditions():
    try:
        nodes = v1.list_node()
        node_conditions = []

        for node in nodes.items:
            has_unknown_condition = False
            for condition in node.status.conditions:
                if condition.type == "Ready" and condition.status == "Unknown" and condition.reason == "NodeStatusUnknown":
                    has_unknown_condition = True

                node_conditions.append({
                    "node_name": node.metadata.name,
                    "condition_type": condition.type,
                    "status": condition.status,
                    "reason": condition.reason,
                    "message": condition.message,
                    "last_heartbeat_time": condition.last_heartbeat_time,
                    "last_transition_time": condition.last_transition_time,
                    "has_unknown_condition": has_unknown_condition  # Flag for the condition
                })

        return node_conditions
    except ApiException as e:
        print(f"Exception when fetching node conditions: {e}")
        return []

def get_node_events():
    try:
        events = v1.list_event_for_all_namespaces()
        node_events = []
        for event in events.items:
            if "Node" in event.involved_object.kind:
                node_events.append({
                    "node_name": event.involved_object.name,
                    "reason": event.reason,
                    "message": event.message,
                    "type": event.type,
                    "first_timestamp": event.first_timestamp,
                    "last_timestamp": event.last_timestamp,
                    "count": event.count
                })
        return node_events
    except ApiException as e:
        print(f"Exception when fetching node events: {e}")
        return []

@app.route('/restart-node/<node_name>', methods=['POST'])
def restart_node(node_name):
    # Get the password from the request
    password = request.json.get('password')
    
    if not password:
        return jsonify({'status': 'Failed', 'message': 'Password is required'}), 400

    # SSH parameters
    worker_node_ip = node_name  # Use the node name as the IP address
    username = 'anvitha'

    # SSH connection
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(worker_node_ip, username=username, password=password)
    except Exception as e:
        return jsonify({'status': 'Failed', 'message': str(e)}), 500

    # Execute the command to restart kubelet
    command = f'echo {password} | sudo -S systemctl restart kubelet'
    stdin, stdout, stderr = ssh.exec_command(command)

    # Wait for the command to complete
    while not stdout.channel.exit_status_ready():
        pass

    # Get the exit status
    exit_status = stdout.channel.recv_exit_status()

    ssh.close()

    # Check if the command succeeded
    if exit_status == 0:
        return jsonify({'status': 'Restarted Success'}), 200
    else:
        return jsonify({'status': 'Failed', 'message': stderr.read().decode()}), 500

##
def restart_pod(pod_name):
    try:
        api_instance = client.CoreV1Api()
        namespace = 'default'
        api_instance.delete_namespaced_pod(name=pod_name, namespace=namespace)
    except ApiException as e:
        print(f"Exception when calling CoreV1Api->delete_namespaced_pod: {e}")


@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def handle_login():
    error_message = None  # Initialize error_message variable
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Basic validation
        if not username or not password:
            error_message = 'Please enter both username and password.'
        else:
            # Replace with your actual authentication logic (e.g., database check)
            if username == 'admin' and password == 'admin':
                return redirect(url_for('welcome'))  # Redirect to welcome page
            else:
                error_message = 'Invalid username or password.'

    return render_template('login.html', error_message=error_message)

@app.route('/welcome')
def welcome():
    return render_template('welcome.html')  # Simple welcome page content

@app.route('/db_application')
def db_app():
    pod_usages = get_pod_cpu_memory_usage(v1, namespace, label_selectors)
    alerts = []
    for pod in pod_usages:
        selector = pod[5] 
        thresholds = label_selectors.get(selector, {})
        if pod[2] > thresholds.get("cpu", float("inf")) or pod[4] > thresholds.get("memory", float("inf")):
            alerts.append(pod)
    return render_template('alerts.html', pod_usages=pod_usages, alerts=alerts)

@app.route('/restart_db', methods=['POST'])
def restart_db():
    pod_name = request.form['pod_name']
    restart_pod_manager(v1, namespace, pod_name)
    return redirect(url_for('db_app'))

def signal_handler(sig, frame):
    print("Exiting gracefully...")
    sys.exit(0)

@app.route('/cluster')
def cluster():
     return render_template('index.html')

@app.route('/nodes')
def check_nodes():
    node_metrics = get_node_metrics()
    return render_template('node_metrics.html', node_metrics=node_metrics)
    
@app.route('/pods')
def check_pods():
    pod_metrics = get_pod_metrics()
    return render_template('pod_metrics.html', pod_metrics=pod_metrics)

def get_pod_logs(pod_name):
    try:
        log = v1.read_namespaced_pod_log(name=pod_name, namespace=namespace)
        return log
    except ApiException as e:
        print(f"Exception when calling CoreV1Api->read_namespaced_pod_log: {e}")
        return "Error fetching logs"

@app.route('/pod_logs/<pod_name>', methods=['GET'])
def pod_logs(pod_name):
    log = get_pod_logs(pod_name)
    return log  # Return plain text log

@app.route('/deployments')
def check_deployments():
    deployment_list = get_deployments()
    return render_template('deployments.html', deployments=deployment_list)

@app.route('/services')
def check_services():
    service_list = get_services()
    return render_template('services.html', services=service_list)

@app.route('/namespaces')
def check_namespaces():
    namespace_list = get_namespaces()
    return render_template('namespaces.html', namespaces=namespace_list)

@app.route('/restart', methods=['POST'])
def restart():
    pod_name = request.form['pod_name']
    restart_pod(pod_name)
    return redirect(url_for('cluster'))

@app.route('/check_node_status')
def check_node_status():
    node_conditions = get_node_conditions()
    node_events = get_node_events()
    return render_template('node_status.html', node_conditions=node_conditions, node_events=node_events)


if __name__ == '__main__':
    app.run(debug=True)
