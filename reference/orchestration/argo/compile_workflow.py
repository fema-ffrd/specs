#!/usr/bin/env python3
"""
Orchestration Workflow Compiler

Compiles a JSON workflow definition to YAML workflow format.
"""

import json
import sys
import yaml
from typing import Any, Dict, List


def create_volume_claim_templates(volumes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    templates = []
    for vol in volumes:
        template = {
            "metadata": {
                "name": vol["name"]
            },
            "spec": {
                "accessModes": [vol.get("access_mode", "ReadWriteOnce")],
                "resources": {
                    "requests": {
                        "storage": vol["size"]
                    }
                }
            }
        }
        templates.append(template)
    return templates


def create_volume_mounts(task: Dict[str, Any], volumes: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    mounts = []
    volume_names = task.get("volume_mounts", [vol["name"] for vol in volumes])

    for vol_name in volume_names:
        vol_def = next((v for v in volumes if v["name"] == vol_name), None)
        if vol_def:
            mount = {
                "name": vol_name,
                "mountPath": vol_def.get("mount_path", "/work")
            }
            mounts.append(mount)

    return mounts


def create_task_template(task: Dict[str, Any], volumes: List[Dict[str, Any]]) -> Dict[str, Any]:
    config_json = json.dumps(task["config"])

    container = {
        "image": task["image"],
        "args": [config_json],
        "volumeMounts": create_volume_mounts(task, volumes)
    }

    # Add environment variables if specified
    if "env" in task:
        container["env"] = task["env"]

    template = {
        "name": task["name"],
        "container": container
    }

    return template


def create_dag_tasks(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    dag_tasks = []
    for task in tasks:
        dag_task = {
            "name": task["name"],
            "template": task["name"]
        }

        dependencies = task.get("dependencies", [])
        if dependencies:
            dag_task["dependencies"] = dependencies

        dag_tasks.append(dag_task)

    return dag_tasks


def compile_workflow(config: Dict[str, Any]) -> Dict[str, Any]:
    workflow = {
        "apiVersion": "argoproj.io/v1alpha1",
        "kind": "Workflow",
        "metadata": {
            "generateName": f"{config['workflow_name']}-"
        },
        "spec": {
            "entrypoint": config.get("entrypoint", "main"),
            "volumeClaimTemplates": create_volume_claim_templates(config["volumes"]),
            "templates": []
        }
    }

    main_template = {
        "name": config.get("entrypoint", "main"),
        "dag": {
            "tasks": create_dag_tasks(config["tasks"])
        }
    }
    workflow["spec"]["templates"].append(main_template)

    for task in config["tasks"]:
        task_template = create_task_template(task, config["volumes"])
        workflow["spec"]["templates"].append(task_template)

    return workflow


def main():
    if len(sys.argv) > 1:
        config_json = "".join(sys.argv[1:])
    else:
        config_json = sys.stdin.read()

    try:
        config = json.loads(config_json)
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        workflow = compile_workflow(config)
    except KeyError as e:
        print(f"❌ Missing required field: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error compiling workflow: {e}", file=sys.stderr)
        sys.exit(1)

    yaml_content = yaml.dump(workflow, default_flow_style=False, sort_keys=False, allow_unicode=True)
    print(yaml_content)


if __name__ == "__main__":
    main()
