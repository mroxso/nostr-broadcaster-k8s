import uuid
from flask import Flask, request, jsonify, render_template
from kubernetes import client, config
import yaml
import os

app = Flask(__name__)

# Load the Kubernetes configuration
if(os.getenv('KUBERNETES_SERVICE_HOST')):
    config.load_incluster_config()
else:
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

@app.route('/jobs', methods=['GET'])
def get_jobs():
    # Get the list of jobs from the Kubernetes cluster
    jobs = api.list_namespaced_job(namespace='default')

    # Return the list of jobs
    return jsonify(jobs.items)

@app.route('/jobs/<job_name>', methods=['GET'])
def get_job(job_name):
    # Get the job from the Kubernetes cluster
    job = api.read_namespaced_job(name=job_name, namespace='default')

    # Return the job
    return jsonify(job)

@app.route('/', methods=['GET'])
def index():
    # return jsonify(message='Hello world')
    return render_template('/sites/index.html')

if __name__ == '__main__':
    app.run(debug=True)