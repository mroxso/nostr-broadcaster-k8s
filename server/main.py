import uuid
from flask import Flask, request, jsonify, render_template
from kubernetes import client, config
import yaml
import os
import json
import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

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
    # Form Data
    publickey = request.form['publickey']
    from_relays = request.form['from_relays']
    to_relay = request.form['to_relay']
    ip = request.remote_addr
    useragent = request.headers.get('User-Agent')
    print("=== FORM DATA ===")
    print("Public Key: " + publickey)
    print("From Relays: " + from_relays)
    print("To Relay: " + to_relay)
    print("IP: " + ip)
    print("User Agent: " + useragent)
    print("=== END FORM DATA ===")

    if(not publickey or not from_relays or not to_relay):
        return jsonify(message='Missing form data')

    # Get the job specification from the YAML file
    with open('job.yaml', 'r') as f:
        job_spec_file = f.read()

    # Convert the YAML specification to a Kubernetes job object
    job_manifest = yaml.safe_load(job_spec_file)
    job = client.V1Job(**job_manifest)
    # add uuid to job name
    job.metadata['name'] += '-' + str(uuid.uuid4())
    # print(job.metadata['name'])

    # Edit the job specification
    job.spec['template']['spec']['containers'][0]['env'][0]['value'] = from_relays
    job.spec['template']['spec']['containers'][0]['env'][1]['value'] = to_relay
    job.spec['template']['spec']['containers'][0]['env'][2]['value'] = publickey
    
    # Create the job on the Kubernetes cluster
    api.create_namespaced_job(body=job, namespace='default')

    # Return a success message
    # return jsonify(message='Job "' + job.metadata['name'] + '" deployed successfully')
    return job.metadata['name']

@app.route('/jobs', methods=['GET'])
def get_jobs():
    # Get the list of jobs from the Kubernetes cluster
    jobs = api.list_namespaced_job(namespace='default')

    # Return the list of jobs
    # return jsonify(jobs.to_dict())
    # return jsonify(jobs.items)
    return (jobs.to_dict()['items'])

@app.route('/job/<job_name>', methods=['GET'])
def get_job(job_name):
    # Get the job from the Kubernetes cluster
    job = api.read_namespaced_job(name=job_name, namespace='default')

    # Return the job
    # return jsonify(job)
    return (job.to_dict())

@app.route('/', methods=['GET'])
def index():
    return render_template('/sites/index.html')

@app.route('/status/<job_name>', methods=['GET'])
def status(job_name):
    job_status = get_job(job_name)['status']

    job_active = job_status['active']
    job_completion_time = job_status['completion_time']
    job_failed = job_status['failed']
    job_ready = job_status['ready']
    job_start_time = job_status['start_time']
    job_succeeded = job_status['succeeded']
    job_uncounted_terminated_pods = job_status['uncounted_terminated_pods']

    return render_template('/sites/status.html', job_name=job_name, job_active=job_active, job_completion_time=job_completion_time, job_failed=job_failed, job_ready=job_ready, job_start_time=job_start_time, job_succeeded=job_succeeded, job_uncounted_terminated_pods=job_uncounted_terminated_pods)

if __name__ == '__main__':
    app.run(debug=True)