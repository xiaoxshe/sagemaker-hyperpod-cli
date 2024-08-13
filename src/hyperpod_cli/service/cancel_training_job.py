# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
from typing import Optional
import subprocess

from hyperpod_cli.clients.kubernetes_client import (
    KubernetesClient,
)
from kubernetes.client.rest import ApiException


class CancelTrainingJob:
    def __init__(self):
        return

    def cancel_training_job(self, job_name: str, namespace: Optional[str]):
        """
        Cancel training job provided by the user in the specified namespace.
        If namespace is not provided job is canceled from the default namespace in user context
        """

        k8s_client = KubernetesClient()

        if not namespace:
            namespace = k8s_client.get_current_context_namespace()
        try:
            result = k8s_client.delete_training_job(
                job_name=job_name, namespace=namespace
            )
        except ApiException as e:
            raise RuntimeError(f"Unexpected API error: {e.reason} ({e.status})")

        helm_chart_cleanup_command = [
            "helm",
            "uninstall",
            job_name,
            "--namespace",
            namespace,
        ]

        if result.get("status") and result.get("status") == "Success":
            subprocess.run(helm_chart_cleanup_command, capture_output=True, text=True)
            return None
        else:
            return result