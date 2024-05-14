import sys
from kubernetes import client, config

config.load_kube_config()

v1 = client.CoreV1Api()

v1.delete_namespaced_pod(namespace='default', name='busy-pod')

#to check pod logs
# pod_logs = v1.read_namespaced_pod_log(name='busy-pod', namespace='default')
# print(pod_logs)