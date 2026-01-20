from kubernetes import client, config, watch
import os
import time
import datetime
import logging

logging.basicConfig(level=logging.INFO)
NS = os.getenv("NAMESPACE", "hello")
CM_NAME = os.getenv("CONFIGMAP_NAME", "hello-app-config")
LABEL_SELECTOR = os.getenv("LABEL_SELECTOR", "app=helloworld")
RETRY_DELAY = 5


def load_k8s_config():
    try:
        config.load_incluster_config()
        logging.info("Loaded in-cluster config")
    except Exception:
        config.load_kube_config()
        logging.info("Loaded kubeconfig")


def restart_deployments(api, apps_api):
    ts = datetime.datetime.utcnow().isoformat() + "Z"
    deps = apps_api.list_namespaced_deployment(
        namespace=NS, label_selector=LABEL_SELECTOR
    )

    if not deps.items:
        logging.warning(
            "No deployments found with selector %s in namespace %s", LABEL_SELECTOR, NS
        )
        return

    for d in deps.items:
        name = d.metadata.name
        patch = {
            "spec": {
                "template": {
                    "metadata": {"annotations": {"configmap-restarted-at": ts}}
                }
            }
        }
        try:
            apps_api.patch_namespaced_deployment(name=name, namespace=NS, body=patch)
            logging.info("Patched deployment %s in %s at %s", name, NS, ts)
        except Exception as e:
            logging.exception("Failed to patch %s: %s", name, e, ts)


def main():
    load_k8s_config()
    core = client.CoreV1Api()
    apps = client.AppsV1Api()
    w = watch.Watch()

    logging.info(
        "Starting watcher for ConfigMap '%s' in namespace '%s' with selector '%s'",
        CM_NAME,
        NS,
        LABEL_SELECTOR,
    )

    while True:
        try:
            stream = w.stream(
                core.list_namespaced_config_map, namespace=NS, timeout_seconds=0
            )
            for ev in stream:
                etype = ev["type"]
                obj = ev["object"]
                name = obj.metadata.name

                if name != CM_NAME:
                    continue

                logging.info("ConfigMap event %s for %s", etype, name)
                if etype in ("ADDED", "MODIFIED"):
                    restart_deployments(core, apps)
        except Exception:
            logging.exception("Watch failed, retrying in %s seconds", RETRY_DELAY)
            time.sleep(RETRY_DELAY)


if __name__ == "__main__":
    main()
