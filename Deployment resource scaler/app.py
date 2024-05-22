from flask import Flask, render_template, request, redirect, url_for
from kubernetes import client, config
from kubernetes.client import V1Pod, V1PodList
from kubernetes.client.rest import ApiException

app = Flask(__name__)

config.load_incluster_config()

# Define default values for resource limits
DEFAULT_CPU_LIMIT = '500m'  # Adjust as necessary
DEFAULT_MEMORY_LIMIT = '512Mi'  # Adjust as necessary

@app.route('/')
def index():
    v1 = client.AppsV1Api()
    deployments = v1.list_deployment_for_all_namespaces().items
    return render_template('index.html', deployments=deployments)

@app.route('/edit/<namespace>/<name>', methods=['GET', 'POST'])
def edit(namespace, name):
    v1 = client.AppsV1Api()
    deployment = v1.read_namespaced_deployment(name, namespace)
    
    if request.method == 'POST':
        if 'reset' in request.form:
            new_cpu = DEFAULT_CPU_LIMIT
            new_memory = DEFAULT_MEMORY_LIMIT
        else:
            new_cpu = request.form['cpu']
            new_memory = request.form['memory']
        
        # Ensure limits dictionary exists
        if not deployment.spec.template.spec.containers[0].resources.limits:
            deployment.spec.template.spec.containers[0].resources.limits = {}

        deployment.spec.template.spec.containers[0].resources.limits['cpu'] = new_cpu
        deployment.spec.template.spec.containers[0].resources.limits['memory'] = new_memory
        
        v1.patch_namespaced_deployment(name, namespace, deployment)
        
        return redirect(url_for('index'))
    
    return render_template('edit.html', deployment=deployment)
@app.route('/pods/<namespace>/<name>')
def pods(namespace, name):
    v1 = client.CoreV1Api()
    try:
        pods_list = v1.list_namespaced_pod(namespace, label_selector=f'app={name}').items
        pods_info = []
        for pod in pods_list:
            pod_name = pod.metadata.name
            pod_metrics = get_pod_metrics(pod_name, namespace)
            cpu_usage = pod_metrics.get('cpu', 'Not available')
            memory_usage = pod_metrics.get('memory', 'Not available')
            pods_info.append({'name': pod_name, 'cpu_usage': cpu_usage, 'memory_usage': memory_usage})
    except ApiException as e:
        pods_info = None

    return render_template('pods.html', deployment_name=name, pods=pods_info)
def convert_cpu_from_nano_to_millicores(cpu_nano):
    if cpu_nano.endswith('n'):
        cpu_nano = cpu_nano[:-1]  # Remove the 'n' suffix
        try:
            return str(int(cpu_nano) / 1000000) + 'm'  # Convert nanocores to millicores
        except ValueError:
            return 'Not available'
    else:
        return 'Not available'  # Return 'Not available' if the suffix is not 'n'

def convert_memory_from_kib_to_mib(memory_kib):
    try:
        if memory_kib.endswith('Ki'):
            memory_kib = memory_kib[:-2]  # Remove the 'Ki' suffix
            return str(int(memory_kib) / 1024) + 'Mi'  # Convert KiB to MiB
        else:
            return 'Not available'  # Return 'Not available' if the suffix is not 'Ki'
    except ValueError:
        return 'Not available'  # Return 'Not available' if conversion fails

def get_pod_metrics(pod_name, namespace):
    
    api_instance = client.CustomObjectsApi()

    try:
        # Make API request to Metrics Server to fetch pod metrics
        metrics = api_instance.list_namespaced_custom_object(
            group="metrics.k8s.io",
            version="v1beta1",
            namespace=namespace,
            plural="pods"
        )
        
        # Search for metrics related to the specific pod
        for item in metrics['items']:
            if item['metadata']['name'] == pod_name:
                cpu_usage_nano = item['containers'][0]['usage']['cpu']
                memory_usage_kib = item['containers'][0]['usage']['memory']
                cpu_usage = convert_cpu_from_nano_to_millicores(cpu_usage_nano)
                memory_usage = convert_memory_from_kib_to_mib(memory_usage_kib)
                return {'cpu': cpu_usage, 'memory': memory_usage}
        
        # If metrics for the pod are not found, return 'Not available'
        return {'cpu': 'Not available', 'memory': 'Not available'}
    
    except ApiException as e:
        print("Exception when calling CustomObjectsApi->list_namespaced_custom_object: %s\n" % e)
        return {'cpu': 'Not available', 'memory': 'Not available'}

if __name__ == '__main__':
    app.run(debug=True)
