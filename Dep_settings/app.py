from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from kubernetes import client, config

app = Flask(__name__)
CORS(app)

config.load_kube_config()

v1 = client.AppsV1Api()
core_v1 = client.CoreV1Api()

def deployment_ready(deployment):
    if deployment.status.ready_replicas is None:
        return False
    return deployment.status.ready_replicas == deployment.status.replicas

@app.route('/')
def index():
    deployments = v1.list_deployment_for_all_namespaces().items
    return render_template('index.html', deployments=deployments, deployment_ready=deployment_ready)

@app.route('/update_deployment', methods=['POST'])
def update_deployment():
    try:
        data = request.form
        name = data['name']
        namespace = data['namespace']
        cpu_limit = data['cpu_limit']
        memory_limit = data['memory_limit']

        # Fetch the current deployment to get the image
        current_deployment = v1.read_namespaced_deployment(name=name, namespace=namespace)
        current_image = current_deployment.spec.template.spec.containers[0].image

        # Patch the deployment with the new resource limits
        body = {
            "spec": {
                "template": {
                    "spec": {
                        "containers": [{
                            "name": current_deployment.spec.template.spec.containers[0].name,
                            "image": current_image,  # Include the current image
                            "resources": {
                                "limits": {
                                    "cpu": cpu_limit,
                                    "memory": memory_limit
                                }
                            }
                        }]
                    }
                }
            }
        }
        v1.patch_namespaced_deployment(name=name, namespace=namespace, body=body)

        # Delete the pods to apply the new resource limits
        pods = core_v1.list_namespaced_pod(namespace=namespace, label_selector=f'app={name}')
        for pod in pods.items:
            core_v1.delete_namespaced_pod(name=pod.metadata.name, namespace=namespace)

        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
