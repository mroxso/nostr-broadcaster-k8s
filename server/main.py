import uuid
from flask import Flask, request, jsonify, render_template, redirect
from kubernetes import client, config
import yaml
import os
import json
import logging
from nostr.key import PublicKey

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
coreApi = client.CoreV1Api()

# Handle POST requests
@app.route('/deploy', methods=['POST'])
def deploy_job():
    # Form Data
    publickey = request.form['publickey']
    if "npub" in publickey:
        publickey = PublicKey.from_npub(publickey).hex()

    from_relays = request.form['from_relays']
    to_relay = request.form['to_relay']
    ip = request.remote_addr
    useragent = request.headers.get('User-Agent')
    print("=== FORM DATA ===")
    print("Public Key (hex): " + publickey)
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
    # return job.metadata['name']
    return redirect('/status/' + job.metadata['name'])

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
    try:
        # Get the job from the Kubernetes cluster
        job = api.read_namespaced_job(name=job_name, namespace='default')

        # Return the job
        # return jsonify(job)
        return (job.to_dict())
    except:
        return jsonify(message='Job not found'), 200
    
# Force Stop Job
@app.route('/job/<job_name>/force-stop', methods=['GET'])
def force_stop_job(job_name):
    # Kubernetes stop job
    try:
        # Delete the job from the Kubernetes cluster
        api.delete_namespaced_job(name=job_name, namespace='default')

        # Delete the job pods from the Kubernetes cluster
        coreApi.delete_collection_namespaced_pod(namespace='default', label_selector='job-name=' + job_name)

        # Return the job
        return jsonify(message='Job "' + job_name + '" deleted successfully'), 200
    except:
        return jsonify(message='Job not found'), 404


@app.route('/', methods=['GET'])
def index():
    return render_template('/sites/index.html')

@app.route('/status/<job_name>', methods=['GET'])
def status(job_name):
    try:
        job_status = get_job(job_name)['status']

        job_active = job_status['active']
        job_completion_time = job_status['completion_time']
        job_failed = job_status['failed']
        job_ready = job_status['ready']
        job_start_time = job_status['start_time']
        job_succeeded = job_status['succeeded']
        job_uncounted_terminated_pods = job_status['uncounted_terminated_pods']

        try:
            # get the list of pods running the job
            job_pods = coreApi.list_namespaced_pod(namespace="default", label_selector=f"job-name={job_name}")
            # assume there is only one pod running the job
            pod_name = job_pods.items[0].metadata.name
            # use the read_namespaced_pod_log method to read the logs of the pod
            job_logs = coreApi.read_namespaced_pod_log(name=pod_name, namespace="default")
            # job_logs = "No logs available"
        except:
            job_logs = "Could not load logs.."
    except:
        job_active = "No job found"
        job_completion_time = "No job found"
        job_failed = "No job found"
        job_ready = "No job found"
        job_start_time = "No job found"
        job_succeeded = "No job found"
        job_uncounted_terminated_pods = "No job found"

        job_logs = "No logs available"

    return render_template('/sites/status.html', job_name=job_name, job_active=job_active, job_completion_time=job_completion_time, job_failed=job_failed, job_ready=job_ready, job_start_time=job_start_time, job_succeeded=job_succeeded, job_uncounted_terminated_pods=job_uncounted_terminated_pods, job_logs=job_logs)

if __name__ == '__main__':
    app.run(debug=True)