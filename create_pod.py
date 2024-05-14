import sys
from kubernetes import client, config

config.load_kube_config()

v1 = client.CoreV1Api()

containers = []
container1 = client.V1Container(name='my-nginx', image='nginx')
containers.append(container1)

pod_spec = client.V1PodSpec(containers=containers)
pod_metadata = client.V1ObjectMeta(name='my-ng-inx', namespace='default')

pod_body = client.V1Pod(api_version='v1', kind='Pod', metadata=pod_metadata, spec=pod_spec)

v1.create_namespaced_pod(namespace='default', body=pod_body)