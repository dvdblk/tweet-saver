# Kubernetes deployment of Tweet Saver

## Environment Variables
The app requires some env variables which can be supplied with a `Secret`:

```
# Namespace
$ kubectl create ns tweet-saver
# Create a Secret resource
$ kubectl create secret generic env-var-secret --from-env-file ../.env -n tweet-saver
```

## Deployment
```
$ kubectl apply -f deployment.yaml
```