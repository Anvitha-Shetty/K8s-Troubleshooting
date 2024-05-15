from flask import Flask, render_template

import subprocess



app = Flask(__name__)



def get_node_metrics():

    try:

        # Run kubectl top node command and capture the output

        command = ["kubectl", "top", "node"]

        output = subprocess.check_output(command).decode("utf-8")

        lines = output.strip().split("\n")[1:]  # Skip the header line

        metrics = []



        for line in lines:

            parts = line.split()

            if len(parts) >= 3:

                node_name = parts[0]

                cpu_usage = parts[1]

                memory_usage = parts[2]

                metrics.append({

                    "node_name": node_name,

                    "cpu_usage": cpu_usage,

                    "memory_usage": memory_usage

                })

            else:

                # Handle unexpected output format

                print("Error: Unexpected output format from kubectl top node command")

                print("Output line:", line)  # Print the problematic line for debugging

        return metrics

    except subprocess.CalledProcessError as e:

        # Handle subprocess error

        print(f"Error executing kubectl top node command: {e}")

        return []



def get_pod_metrics():

    try:

        # Run kubectl top pods command and capture the output

        command = ["kubectl", "top", "pods"]

        output = subprocess.check_output(command).decode("utf-8")

        lines = output.strip().split("\n")[1:]  # Skip the header line

        metrics = []



        for line in lines:

            parts = line.split()

            if len(parts) >= 3:

                pod_name = parts[0]

                cpu_usage = parts[1]

                memory_usage = parts[2]

                metrics.append({

                    "pod_name": pod_name,

                    "cpu_usage": cpu_usage,

                    "memory_usage": memory_usage

                })

            else:

                # Handle unexpected output format

                print("Error: Unexpected output format from kubectl top pods command")

                print("Output line:", line)  # Print the problematic line for debugging

        return metrics

    except subprocess.CalledProcessError as e:

        # Handle subprocess error

        print(f"Error executing kubectl top pods command: {e}")

        return []



@app.route('/')

def index():

    return render_template('index.html')



@app.route('/nodes')

def check_nodes():

    # Get node metrics

    node_metrics = get_node_metrics()

    return render_template('node_metrics.html', node_metrics=node_metrics)



@app.route('/pods')

def check_pods():

    # Get pod metrics

    pod_metrics = get_pod_metrics()

    return render_template('pod_metrics.html', pod_metrics=pod_metrics)



if __name__ == '__main__':

    app.run(debug=True)

