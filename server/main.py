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
    # Define the job specification
    job_spec = '''
    apiVersion: batch/v1
    kind: Job
    metadata:
    name: nostr-broadcaster
    spec:
    ttlSecondsAfterFinished: 100
    template:
        spec:
        containers:
        - name: nostr-broadcast
        image:  'ghcr.io/mroxso/nostr-broadcast:latest'
        env:
          - name: RELAY_FROM_URLS
          value:  'wss://relay.damus.io, wss://relay.nostr.band'
          - name: RELAY_TO_URL
          value:  'wss://nostr.rocks'
          - name: PUBLIC_KEY
          value:  82341f882b6eabcd2ba7f1ef90aad961cf074af15b9ef44a09f9d2a8fbfbe6a2
    backoffLimit: 4
    '''

    # Get the job specification from the YAML file
    with open('job.yaml', 'r') as f:
        job_spec_file = f.read()

    # Convert the YAML specification to a Kubernetes job object
    job_manifest = yaml.safe_load(job_spec_file)
    job = client.V1Job(**job_manifest)

    # Create the job on the Kubernetes cluster
    api.create_namespaced_job(body=job, namespace='default')

    # Return a success message
    return jsonify(message='Job deployed successfully')

if __name__ == '__main__':
    app.run(debug=True)