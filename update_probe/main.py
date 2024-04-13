import datetime
import json
import os.path
import sys
import time
from typing import List, Optional

from kubernetes import client, config
from kubernetes.client import V1PodTemplateSpec, ApiException

KUBECTL_CONFIG_FILES: List[str] = [
    os.path.join(os.environ.get("HOME", ""), ".kube", "config"),
    "/etc/kubernetes/admin.conf"
]

DEFAULT_NAMESPACE: str = "test"

DEFAULT_JOB_NAME_PREFIX: str = "odoo-update-base"
DEFAULT_JOB_NAME_SUFFIX: str = "job"
DEFAULT_JOB_TEMPLATE_NAME: str = f"{DEFAULT_NAMESPACE}-backend-base-update"

DEFAULT_JOB_MAX_ITERATIONS: int = 60


def log_step(message: str) -> None:
    print(message)


def log(message: str) -> None:
    print(f" - {message}")


class BaseUpdateProbe:
    _namespace: str

    _job_name_prefix: str
    _job_name_suffix: str
    _job_template_name: str

    _max_iterations: int

    _kube_batch: Optional[client.BatchV1Api]
    _kube_core: Optional[client.CoreV1Api]

    _current_job_name: str

    def __init__(self) -> None:
        super().__init__()

        self._namespace = os.environ.get("NAMESPACE", DEFAULT_NAMESPACE)

        self._job_name_prefix = os.environ.get("JOB_NAME_PREFIX", DEFAULT_JOB_NAME_PREFIX)
        self._job_name_suffix = os.environ.get("JOB_NAME_SUFFIX", DEFAULT_JOB_NAME_SUFFIX)
        self._job_template_name = os.environ.get("JOB_TEMPLATE_NAME", DEFAULT_JOB_TEMPLATE_NAME)

        self._max_iterations = int(os.environ.get("JOB_MAX_ITERATIONS", DEFAULT_JOB_MAX_ITERATIONS))

        self._kube_batch = None
        self._kube_core = None

        self._current_job_name = ""

    def run(self) -> bool:
        try:
            self._compute_current_namespace()

            self._configure_kube_clients()

            self._init_kube_clients()

            self._create_job_if_not_running_save_current_job_name()
            if not self._current_job_name:
                raise ValueError("Invalid current Job name")

            self._wait_for_job_completion()

            return self._check_completed_job_status()

        except ApiException as e:
            print(json.dumps(json.loads(e.body), indent=2))
            return False

        except Exception as e:
            print(f"*** EXCEPTION *** {e}")
            return False

    def _compute_current_namespace(self) -> None:
        log_step("Computing current namespace")

        namespace_file_path: str = "/var/run/secrets/kubernetes.io/serviceaccount/namespace"

        if os.path.exists(namespace_file_path):
            log(f"Reading namespace from {namespace_file_path}")
            with open(namespace_file_path, "r") as fd:
                self._namespace = fd.read().strip()

        log(f"Computed namespace: {self._namespace}")

    def _configure_kube_clients(self) -> None:
        log_step("Configuring k8s clients")

        try:
            log("Trying to load in cluster config")
            config.load_incluster_config()
            return

        except Exception as e:
            log(f"Unable to load ServiceAccount configuration: {e}")

        config_dict: dict = dict()

        for config_file_path in KUBECTL_CONFIG_FILES:
            if os.path.exists(config_file_path):
                log(f"Trying to load config from {config_file_path}")
                with open(config_file_path, "r") as fd:
                    config_dict = json.loads(fd.read())
                    break

        if not config_dict:
            raise ValueError("Kubectl configuration not found")

        log(f"Loading config")
        config.load_kube_config_from_dict(config_dict=config_dict)

    def _init_kube_clients(self) -> None:
        log_step("Initializing k8s clients")

        log(f"Creating BatchV1Api")
        self._kube_batch = client.BatchV1Api()
        if self._kube_batch is None:
            raise ValueError("Unable to create BatchV1Api")

        log(f"Creating CoreV1Api")
        self._kube_core = client.CoreV1Api()
        if self._kube_core is None:
            raise ValueError("Unable to create CoreV1Api")

    def _create_job_if_not_running_save_current_job_name(self) -> None:
        log_step("Creating new Job (if not already running)")

        active_jobs = self._get_jobs()
        log(f"Active jobs count: {len(active_jobs)}")

        if len(active_jobs) == 1:
            active_job = active_jobs[0]
            self._current_job_name = active_job.metadata.name
            log(f"Job already found: {self._current_job_name}")
            return

        if len(active_jobs) > 1:
            raise ValueError("Multiple job running")

        log(f"Reading Job template: {self._job_template_name}")
        pod_template: V1PodTemplateSpec = self._kube_core.read_namespaced_pod_template(
            namespace=self._namespace,
            name=self._job_template_name
        )

        log(f"Computing job name")
        dt_now: datetime.datetime = datetime.datetime.now()
        date_tag: str = dt_now.strftime("%Y%m%d")
        time_tag: str = dt_now.strftime("%H%M%S")
        job_name: str = "-".join([self._job_name_prefix, date_tag, time_tag, self._job_name_suffix])

        log(f"Creating job")
        job_meta = client.V1ObjectMeta(name=job_name)
        job_spec = client.V1JobSpec(template=pod_template.template, backoff_limit=1, completions=1, parallelism=1)
        job = client.V1Job(api_version="batch/v1", kind="Job", metadata=job_meta, spec=job_spec)
        self._kube_batch.create_namespaced_job(namespace=self._namespace, body=job)

        log(f"Job \"{job_name}\" started in namespace \"{self._namespace}\"")

        self._current_job_name = job_name

    def _wait_for_job_completion(self) -> None:
        log_step("Waiting for Job completion")

        iteration_count: int = 0
        job = self._get_jobs()[-1]

        while iteration_count < self._max_iterations:
            if all([x.status.active is None for x in self._get_jobs()]):
                log("Job completed")
                return

            log(f"Waiting Job conclusion... Iteration {iteration_count}")
            time.sleep(1.0)
            iteration_count += 1

    def _check_completed_job_status(self) -> bool:
        log_step("Checking if completed Job had terminated correctly")

        completed_job = list(filter(lambda x: x.metadata.name == self._current_job_name, self._get_jobs()))[-1]
        if not completed_job:
            raise ValueError("Completed job not found")

        log(f"Job succeeded: {completed_job.status.succeeded}")
        job_result = bool(completed_job.status.succeeded)

        return job_result

    def _get_jobs(self) -> list:
        job_list_full = self._kube_batch.list_namespaced_job(namespace=self._namespace).items
        return list(filter(lambda x: x.metadata.name.startswith(self._job_name_prefix), job_list_full))


if __name__ == "__main__":
    probe = BaseUpdateProbe()
    sys.exit(0 if probe.run() else -1)
