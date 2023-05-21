import uuid
from flask import Flask, request, jsonify
from kubernetes import client, config
import yaml

app = Flask(__name__)

# Load the Kubernetes configuration
config.load_kube_config()

# Get the Kubernetes API client
api = client.BatchV1Api()

# Handle POST requests
@app.route('/deploy', methods=['POST'])
def deploy_job():
    # Get the job specification from the YAML file
    with open('job.yaml', 'r') as f:
        job_spec_file = f.read()

    # Convert the YAML specification to a Kubernetes job object
    job_manifest = yaml.safe_load(job_spec_file)
    job = client.V1Job(**job_manifest)
    # add uuid to job name
    job.metadata['name'] += '-' + str(uuid.uuid4())
    # print(job.metadata['name'])

    # Create the job on the Kubernetes cluster
    api.create_namespaced_job(body=job, namespace='default')

    # Return a success message
    return jsonify(message='Job "' + job.metadata['name'] + '" deployed successfully')

if __name__ == '__main__':
    app.run(debug=True)