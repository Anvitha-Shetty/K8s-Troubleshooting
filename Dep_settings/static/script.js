function editDeployment(name, namespace) {
    const form = document.getElementById('deployment-form');
    const deploymentNameInput = document.getElementById('deployment-name');
    const deploymentNamespaceInput = document.getElementById('deployment-namespace');
    
    deploymentNameInput.value = name;
    deploymentNamespaceInput.value = namespace;

    form.style.display = 'block';
}

document.getElementById('update-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);
    const data = {};

    formData.forEach((value, key) => {
        data[key] = value;
    });

    fetch('/update_deployment', {
        method: 'POST',
        body: new URLSearchParams(formData)
    })
    .then(response => response.json())
    .then(data => {
        alert(data.status);
        form.reset();
        document.getElementById('deployment-form').style.display = 'none';
        location.reload();
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
