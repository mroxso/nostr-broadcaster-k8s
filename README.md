# nostr-broadcaster-k8s
A Broadcaster for Nostr Events (Transmits Events from one Relay to another)

# Usage
Simply login to your Kubernetes Cluster and run the following command:
```bash
kubectl apply -f job_example.yaml
```

You can see the logs with the following command:
```bash
kubectl logs -f job/nostr-broadcaster
```