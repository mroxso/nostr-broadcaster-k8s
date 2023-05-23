# nostr-broadcaster-k8s
A Broadcaster for Nostr Events (Transmits Events from one Relay to another)

# Usage without Kubernetes (Docker only)
```
git clone git@github.com:mroxso/nostr-broadcaster-k8s.git
docker build -t nostr-broadcaster-k8s-server:local server/
docker run --rm --volume <PATH-TO-YOUR-.KUBE-FOLDER>:/root/.kube/ -p 5000:5000 nostr-broadcaster-k8s-server:local
```

# Deploy in Kubernetes
coming soon

# Deploy a sample Job manually
Simply login to your Kubernetes Cluster and run the following command:
```bash
kubectl apply -f job_example.yaml
```

You can see the logs with the following command:
```bash
kubectl logs -f job/nostr-broadcaster
```