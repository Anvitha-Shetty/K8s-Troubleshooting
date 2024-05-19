function editDeployment(name, namespace) {
    const modal = document.getElementById('deployment-form-modal');
    const deploymentNameInput = document.getElementById('deployment-name');
    const deploymentNamespaceInput = document.getElementById('deployment-namespace');
    
    deploymentNameInput.value = name;
    deploymentNamespaceInput.value = namespace;

    modal.style.display = 'block';
}

document.getElementById('update-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    fetch('/update_deployment', {
        method: 'POST',
        body: new URLSearchParams(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Deployment updated successfully.');
        } else {
            alert(`Error: ${data.message}`);
        }
        form.reset();
        document.getElementById('deployment-form-modal').style.display = 'none';
        location.reload();
    })
    .catch(error => {
        console.error('Error:', error);
    });
});

const modal = document.getElementById('deployment-form-modal');
const span = document.getElementsByClassName('close')[0];

span.onclick = function() {
    modal.style.display = 'none';
}

window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = 'none';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const notReadyRows = document.querySelectorAll('tr.not-ready');
    if (notReadyRows.length > 0) {
        const alertBox = document.getElementById('alert');
        alertBox.textContent = 'Some deployments are not ready and require more CPU and memory.';
        alertBox.style.display = 'block';
    }
});
