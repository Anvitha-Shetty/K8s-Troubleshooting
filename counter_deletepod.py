import sys

import json

from kubernetes import client, config



def get_last_digit_from_count_file(filename):

    with open(filename, 'r') as file:

        data = json.load(file)

        last_digit = int(data["data"]["result"][0]["value"][1])

        return last_digit



def get_matching_pod_name(namespace, label_selector):

    config.load_kube_config()

    v1 = client.CoreV1Api()

    pod_list = v1.list_namespaced_pod(namespace, label_selector=label_selector)

    if pod_list.items:

        return pod_list.items[0].metadata.name  

    else:

        raise Exception("No pods found matching the label selector.")



def delete_pod_if_needed(namespace, pod_name):

    config.load_kube_config()

    v1 = client.CoreV1Api()

    v1.delete_namespaced_pod(namespace=namespace, name=pod_name)

    print(f"Deleted pod {pod_name} in namespace {namespace}")



if __name__ == "__main__":

    count_filename = "count.txt"

    namespace = "default"

    label_selector = "app=mongodb"  



    try:

        last_digit = get_last_digit_from_count_file(count_filename)

        if last_digit > 2:

            pod_name = get_matching_pod_name(namespace, label_selector)

            delete_pod_if_needed(namespace, pod_name)

        else:

            print("Last digit is not greater than 2. Pod will not be deleted.")

    except FileNotFoundError:

        print(f"Count file '{count_filename}' not found.")

    except Exception as e:

        print(f"An error occurred: {e}")

