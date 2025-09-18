#!/usr/bin/env python3
import sys
import os
import json
import re
import subprocess
import shutil
import time


def extract_args(argv):
    if len(argv) == 2:
        cfg = argv[1]
        try:
            cfg_json = json.loads(cfg)
            ras = cfg_json.get("ras_schema", {})
            modeldir = ras.get("model_directory")
            model = ras.get("model_name")
            plan_id = ras.get("plan_id")
        except Exception:
            modeldir = model = plan_id = None
    elif len(argv) >= 4:
        modeldir, model, plan_id = argv[1], argv[2], argv[3]
    else:
        modeldir = model = plan_id = None
    return modeldir, model, plan_id


def normalize_plan_id(plan_id):
    if plan_id is None:
        return "00"
    digits = re.sub(r"[^0-9]", "", str(plan_id))
    digits = re.sub(r"^0+", "", digits)
    if digits == "":
        digits = "0"
    return f"{int(digits):02d}"


def main(argv):
    modeldir, model, plan_id = extract_args(argv)
    if not (modeldir and model and plan_id is not None):
        sys.stderr.write(
            "Usage: run-model.py '{\"ras_schema\":{...}}'  OR  run-model.py <model_directory> <model_name> <plan_id>\n"
        )
        return 2

    index_padded = normalize_plan_id(plan_id)

    # set environment variables similarly to the shell script
    env = os.environ.copy()
    ras_lib_path = "/ras/libs:/ras/libs/mkl:/ras/libs/rhel_8"
    ld = env.get("LD_LIBRARY_PATH", "")
    env["LD_LIBRARY_PATH"] = ras_lib_path + (os.pathsep + ld if ld else "")
    ras_exe_path = "/ras/bin"
    path = env.get("PATH", "")
    env["PATH"] = ras_exe_path + (os.pathsep + path if path else "")

    try:
        os.chdir(modeldir)
    except Exception as e:
        sys.stderr.write(f"Error: cannot change directory to {modeldir}: {e}\n")
        return 2

    tmp_name = f"{model}.p{index_padded}.tmp.hdf"
    final_name = f"{model}.p{index_padded}.hdf"
    arg2 = f"x{index_padded}"
    cmd = ["RasUnsteady", tmp_name, arg2]

    # Run RasUnsteady, stream output to stderr and check for success string
    success_phrase = "Finished Unsteady Flow Simulation"
    found_success = False

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, text=True, bufsize=1)
    try:
        for line in proc.stdout:
            sys.stderr.write(line)
            sys.stderr.flush()
            if success_phrase in line:
                found_success = True
        proc.wait()
    except KeyboardInterrupt:
        proc.kill()
        proc.wait()
        sys.stderr.write("Interrupted\n")
        return 2

    if found_success and proc.returncode == 0:
        # mimic sleep and mv behavior
        time.sleep(2)
        try:
            shutil.move(tmp_name, final_name)
            sys.stdout.write(f"RasUnsteady succeeded — moved to {final_name}\n")
            return 0
        except Exception as e:
            sys.stderr.write(f"Error moving file: {e}\n")
            return 2
    else:
        sys.stderr.write("Error: RasUnsteady failed.\n")
        return 2


if __name__ == "__main__":
    exit_code = main(sys.argv)
    sys.exit(exit_code)
