from kubernetes import client, config



config.load_kube_config()



v1 = client.CoreV1Api()



print("Listing nodes with their IPs:")

ret = v1.list_node(watch=False)

for node in ret.items:



    addresses = node.status.addresses

    node_ip = None

    for addr in addresses:

        if addr.type == "InternalIP":

            node_ip = addr.address

            break



    print("%s\t%s" % (node_ip, node.metadata.name))



