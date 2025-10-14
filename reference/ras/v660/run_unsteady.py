#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import traceback
import logging
import structlog
import shutil
from pathlib import Path
from functools import wraps

# -------------------------------------------------
# Paths & constants
# -------------------------------------------------
DOWNLOAD = "/usr/local/bin/download"
UPLOAD = "/usr/local/bin/upload"
RESOLVE = "/usr/local/bin/resolve-config"

LOCAL_DIR = "/mnt"
LOCAL_OUTPUT_DIR = f"{LOCAL_DIR}/output"
LOG_FILE = "app.log"

# -------------------------------------------------
# Force known working log path
# -------------------------------------------------
LOG_DIR = "/mnt/logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "app.log")

# -------------------------------------------------
# Configure logging (flush-safe)
# -------------------------------------------------
class FlushFileHandler(logging.FileHandler):
    def emit(self, record):
        super().emit(record)
        self.flush()

# -------------------------------------------------
# Logging setup (simple, reliable JSON logging)
# -------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[
        FlushFileHandler(LOG_FILE, mode="a", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    cache_logger_on_first_use=True,
)

log = structlog.get_logger()
#log.info("logger_initialized", log_file=LOG_FILE)

# -------------------------------------------------
# Global exception handler
# -------------------------------------------------
def log_uncaught_exceptions(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    log.error(
        "uncaught_exception",
        exception=str(exc_value),
        traceback="".join(traceback.format_exception(exc_type, exc_value, exc_traceback)),
    )

sys.excepthook = log_uncaught_exceptions

# -------------------------------------------------
# Decorator for automatic exception logging
# -------------------------------------------------
def log_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log.error(
                "caught_exception",
                function=func.__name__,
                exception=str(e),
                traceback=traceback.format_exc(),
            )
            print(f"⚠️ Error in {func.__name__}: see {LOG_FILE} for details")
            return None
    return wrapper

# -------------------------------------------------
# Environment setup
# -------------------------------------------------
def setup_environment():
    env = os.environ.copy()
    ras_lib_path = "/ras/libs:/ras/libs/mkl:/ras/libs/rhel_8"
    env["LD_LIBRARY_PATH"] = ras_lib_path + (":" + env.get("LD_LIBRARY_PATH", "")) if env.get("LD_LIBRARY_PATH") else ras_lib_path
    ras_exe_path = "/ras/bin"
    env["PATH"] = ras_exe_path + (":" + env.get("PATH", "")) if env.get("PATH") else ras_exe_path
    return env, ras_exe_path

# -------------------------------------------------
# S3 file processing (download/upload)
# -------------------------------------------------
def process_s3_files(action, files, store_root, paths, command):
    try:
        for file_type in files:
            file_path = paths.get(file_type)
            if not file_path:
                continue

            s3_path = f"s3://{store_root}/{file_path}"
            local_path = f"{LOCAL_DIR}/{file_path}"

            if action == "download":
                subprocess.call([command, file_type, s3_path, local_path])
            elif action == "upload":
                subprocess.call([command, s3_path, "--path", local_path])
        return True
    except Exception as e:
        log.error("process_s3_files_failed", action=action, error=str(e))
        return False

# -------------------------------------------------
# Utility helpers
# -------------------------------------------------
def get_input_by_name(cfg, name):
    return next((i for i in cfg.get("inputs", []) if i.get("name") == name), None)

def get_output_by_name(cfg, name):
    return next((o for o in cfg.get("outputs", []) if o.get("name") == name), None)

def create_local_output_paths(paths_dict, local_root):
    return {k: f"{local_root}/{Path(v).name}" for k, v in paths_dict.items() if v}

# -------------------------------------------------
# File verification
# -------------------------------------------------
def verify_local_files(file_object):
    try:
        paths = file_object.get("paths", {})
        missing = []
        for file_path in paths.values():
            if file_path:
                full_path = f"{LOCAL_DIR}/{file_path}"
                if not os.path.exists(full_path):
                    missing.append(full_path)
        if missing:
            for f in missing:
                log.error("missing_file", file=f)
            return False
        log.info("all_files_verified")
        return True
    except Exception as e:
        log.error("verify_local_files_error", error=str(e))
        return False

# -------------------------------------------------
# Download input
# -------------------------------------------------
def download_s3_input(cfg, input_names):
    for name in input_names:
        files = get_input_by_name(cfg, name)
        if not files:
            log.error("missing_input", name=name)
            continue
        file_types = [k for k, v in files["paths"].items() if v]
        process_s3_files("download", file_types, files["store_root"], files["paths"], DOWNLOAD)
    return True

# -------------------------------------------------
# Process outputs (upload or copy)
# -------------------------------------------------
def process_output_files(cfg, output_names, local_source, action, destination_dir=None):
    for name in output_names:
        output = get_output_by_name(cfg, name)
        if not output:
            log.error("output_not_found", name=name)
            continue

        local_paths = create_local_output_paths(output["paths"], str(local_source))
        file_types = [k for k, v in output["paths"].items() if v]

        for file_type in file_types:
            local_path = local_paths[file_type]
            if not os.path.exists(local_path):
                log.error("missing_local_output", file=local_path)
                continue

            if action == "upload":
                s3_path = f"s3://{output['store_root']}/{output['paths'][file_type]}"
                subprocess.call([UPLOAD, s3_path, "--path", local_path])
                log.info("uploaded_file", file=local_path, destination=s3_path)
            elif action == "copy" and destination_dir:
                dest_path = os.path.join(destination_dir, os.path.basename(local_path))
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                subprocess.call(["cp", local_path, dest_path])
                log.info("copied_file", src=local_path, dest=dest_path)
    return True

# -------------------------------------------------
# Main logic
# -------------------------------------------------
@log_exceptions
def main(cfg):
    env, ras_exe_path = setup_environment()

    model_files = get_input_by_name(cfg, "ras_model_files")
    if not model_files:
        log.error("missing_ras_model_files")
        return 1

    local_tmp_hdf = f"{LOCAL_DIR}/{model_files['paths']['tmp_hdf']}"
    hdf_file = local_tmp_hdf.replace(".tmp", "")
    local_root = Path(local_tmp_hdf).parent
    attrs = cfg["attributes"]

# -------------------------------------------------
# Process inputs
# -------------------------------------------------    
    for input_item in cfg.get("inputs", []):
        if input_item["store_type"] == "S3":
            download_s3_input(cfg, [input_item["name"]])
        elif input_item["store_type"] == "FS":
            log.info("skipped_verification", input=input_item["name"])
        else:
            log.error("unsupported_store_type", store_type=input_item["store_type"])

# -------------------------------------------------
# Clean Data
# -------------------------------------------------
    try:
        shutil.rmtree("/mnt/output")
        log.info("Deleted Output Directory")
    except Exception as e:
        log.error("Delete Output Directory Failed", error=str(e))

    try:
        subprocess.run(["python3", "delete_hdf5_group.py", hdf_file], check=False)
        log.info("Cleaned Data")
    except Exception as e:
        log.error("Cleanup Failed", error=str(e))

# -------------------------------------------------
# Create tmp file if doesn't exist
# -------------------------------------------------
    try:
        if not os.path.exists(local_tmp_hdf):
            os.rename(hdf_file, local_tmp_hdf)
            log.info(f"Renamed HDF File {hdf_file} to {local_tmp_hdf}" )

    except Exception as e:
        log.error("HDF Rename Failed", error=str(e))

# -------------------------------------------------
# Run RasUnsteady
# -------------------------------------------------   
    cmd = [f"{ras_exe_path}/RasUnsteady", local_tmp_hdf, f"x{attrs['geom']}"]
    success_phrase = "Finished Unsteady Flow Simulation"
    found_success = False

    log.info("starting_ras_unsteady", cmd=" ".join(cmd))

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, text=True)
    try:
        for line in proc.stdout:
            sys.stderr.write(line)
            sys.stderr.flush()
            if success_phrase in line:
                found_success = True
        proc.wait()
    except KeyboardInterrupt:
        proc.kill()
        log.error("interrupted")
        return 2

    if not found_success or proc.returncode != 0:
        log.error("ras_unsteady_failed", code=proc.returncode)
        return 2

    # Copy .tmp.hdf → .hdf
    try:
        subprocess.call(["cp", local_tmp_hdf, local_tmp_hdf.replace(".tmp.hdf", ".hdf")])
        log.info("hdf_copied")
    except Exception as e:
        log.error("hdf_copy_failed", error=str(e))

    # Process outputs
    for output in cfg.get("outputs", []):
        if output["store_type"] == "S3":
            process_output_files(cfg, [output["name"]], local_source=local_root, action="upload")
        elif output["store_type"] == "FS":
            process_output_files(cfg, [output["name"]], local_source=local_root, action="copy", destination_dir=LOCAL_OUTPUT_DIR)
        else:
            log.error("unsupported_output_type", store_type=output["store_type"])

    log.info("ras_unsteady_completed")
    return 0

# -------------------------------------------------
# Entry point
# -------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: main.py '<config_json>'")
        sys.exit(1)

    config_json = "".join(sys.argv[1:])

    try:
        result = subprocess.run([RESOLVE, config_json], capture_output=True, text=True, check=True)
        resolved_config = json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ Configuration resolution failed: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse resolved configuration: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

    exit_code = main(resolved_config)
    sys.exit(exit_code)
