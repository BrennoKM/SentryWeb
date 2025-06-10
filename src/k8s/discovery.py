from kubernetes import client, config
import os


def get_current_namespace():
    try:
        with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace") as f:
            return f.read().strip()
    except Exception:
        return os.environ.get("POD_NAMESPACE", "default")  # fallback para testes

def get_total_schedulers():
    try:
        # Dentro do cluster
        config.load_incluster_config()
    except:
        # Para testes locais
        config.load_kube_config()

    v1 = client.CoreV1Api()

    namespace = get_current_namespace()
    label_selector = "app=scheduler"

    pods = v1.list_namespaced_pod(namespace=namespace, label_selector=label_selector)

    running_pods = [
        p for p in pods.items
        if p.status.phase == "Running"
    ]
    TOTAL_SCHEDULERS = len(running_pods)
    return TOTAL_SCHEDULERS if TOTAL_SCHEDULERS > 0 else 1  # Garante que sempre tenha pelo menos 1 scheduler ativo
