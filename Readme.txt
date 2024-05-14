//on master node terminal

sudo apt update
sudo apt install python3 python3-pip

//if encounter dpkg error 

sudo dpkg --configure -a

//then again run
sudo apt update
sudo apt install python3 python3-pip

//install kubernetes python client 
pip3 install kubernetes


kubectl proxy --port=8080 &

//after creating the python file run
python3 k8s_access.py

//use the following command to export counter metrics from prometheus to text file
curl -s http://<Prometheus_cluster_ip>:9090/api/v1/query?query=forms_submitted_counter_total > count.txt
