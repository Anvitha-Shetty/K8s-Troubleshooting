from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from kubernetes import client, config
import subprocess

app = Flask(__name__)
CORS(app)

config.load_kube_config()

v1 = client.AppsV1Api()
metrics_api = client.CustomObjectsApi()

@app.route('/')
def index():
    deployments = v1.list_deployment_for_all_namespaces().items
    return render_template('index.html', deployments=deployments)

@app.route('/update_deployment', methods=['POST'])
def update_deployment():
    data = request.form
    name = data['name']
    namespace = data['namespace']
    replicas = int(data['replicas'])
    cpu_limit = data['cpu_limit']
    memory_limit = data['memory_limit']

    # Execute kubectl command to update the deployment
    command = f"kubectl scale deployment/{name} --replicas={replicas} -n {namespace}"
    subprocess.run(command, shell=True)

    if cpu_limit:
        command = f"kubectl set resources deployment/{name} --limits=cpu={cpu_limit} -n {namespace}"
        subprocess.run(command, shell=True)

    if memory_limit:
        command = f"kubectl set resources deployment/{name} --limits=memory={memory_limit} -n {namespace}"
        subprocess.run(command, shell=True)

    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
