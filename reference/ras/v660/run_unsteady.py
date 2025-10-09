#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import time
from pathlib import Path

DOWNLOAD = "/usr/local/bin/download"
UPLOAD = "/usr/local/bin/upload"
RESOLVE = "/usr/local/bin/resolve-config"

LOCAL_DIR = "/mnt"
LOCAL_OUTPUT_DIR = f"/{LOCAL_DIR}/output"


def setup_environment():
    """Set up the environment for RasUnsteady."""
    env = os.environ.copy()
    ras_lib_path = "/ras/libs:/ras/libs/mkl:/ras/libs/rhel_8"
    ld = env.get("LD_LIBRARY_PATH", "")
    env["LD_LIBRARY_PATH"] = ras_lib_path + (os.pathsep + ld if ld else "")
    ras_exe_path = "/ras/bin"
    path = env.get("PATH", "")
    env["PATH"] = ras_exe_path + (os.pathsep + path if path else "")
    return env, ras_exe_path


def process_s3_files(action, files, store_root, paths, command, local_tmp_hdf=None):
    """
    Generic function to process files (download/upload) from/to S3.

    Args:
        action (str): Action being performed ("download" or "upload").
        files (list): List of file types to process.
        store_root (str): Base S3 path or local directory.
        paths (dict): Dictionary containing file paths.
        command (str): Command to execute (DOWNLOAD or UPLOAD).
    """
    try:
        for file_type in files:
            file_path = paths.get(file_type)
            if not file_path:
                continue  # Skip if the file path is None

            s3_path = f"s3://{store_root}/{file_path}"
            local_path = f"{LOCAL_DIR}/{file_path}"

            if action == "download":
                subprocess.call([command, file_type, s3_path, local_path])
            elif action == "upload":
                subprocess.call([command, s3_path, "--path", local_path])
        return True
    except Exception as e:
        print(f"❌ Error during {action}: {e}")
        return False


def download_s3_input(cfg, input_names: list):
    """
    Download input files from S3 based on the provided configuration and input name.

    Args:
        cfg (dict): The resolved configuration dictionary.
        input_names (list): List of input names to download.
    """
    for input_name in input_names:
        files = get_input_by_name(cfg, input_name)
        if not files:
            print(f"❌ Input '{input_name}' not found in the configuration.")
            return None

        file_types = [key for key, value in files["paths"].items() if value]

        process_s3_files("download", file_types, files["store_root"], files["paths"], DOWNLOAD)
    return True


def create_local_output_paths(paths_dict: dict, local_root: str, local_prefix: str = None) -> dict:
    """
    Create local output paths based on the given local source directory.

    Args:
        paths_dict (dict): Dictionary containing file paths.
        local_root (str): The base directory for local output paths.
        local_prefix (str, optional): Optional prefix for local paths.

    Returns:
        dict: A dictionary mapping output file types to their local paths.
    """
    local_paths = {}
    for field_name, file_path in paths_dict.items():
        if file_path and local_prefix:
            file_name = Path(file_path).name
            local_paths[field_name] = f"{local_root}/{local_prefix}/{file_name}"
        elif file_path:
            file_name = Path(file_path).name
            local_paths[field_name] = f"{local_root}/{file_name}"
    return local_paths


def process_output_files(cfg, output_names: list, local_source: str, action: str, destination_dir: str = None):
    """
    Process output files based on the provided configuration and action.

    Args:
        cfg (dict): The resolved configuration dictionary.
        output_names (list): The names of the outputs to process.
        local_source (str): The base directory for local output paths.
        action (str): The action to perform ("upload" or "copy").
        destination_dir (str, optional): The destination directory for copying files (required for "copy").
    """
    for output_name in output_names:
        # Retrieve the output by name
        output = get_output_by_name(cfg, output_name)
        if not output:
            print(f"❌ Output '{output_name}' not found in the configuration.")
            return False

        # Generate local paths for the output files
        local_paths = create_local_output_paths(output["paths"], str(local_source))

        # Get the file types dynamically from the paths dictionary
        file_types = [key for key, value in output["paths"].items() if value]

        # Process the files based on the action
        try:
            for file_type in file_types:
                local_path = local_paths[file_type]
                if not local_path or not os.path.exists(local_path):
                    print(f"❌ Local file not found: {local_path}")
                    return False

                if action == "upload":
                    s3_path = f"s3://{output['store_root']}/{output['paths'][file_type]}"
                    subprocess.call([UPLOAD, s3_path, "--path", local_path])
                    print(f"✅ Uploaded {file_type} to {s3_path}")
                elif action == "copy" and destination_dir:
                    destination_path = os.path.join(destination_dir, os.path.basename(local_path))
                    os.makedirs(os.path.dirname(destination_path), exist_ok=True)
                    subprocess.call(["cp", local_path, destination_path])
                    print(f"✅ Copied {file_type} to {destination_path}")
        except Exception as e:
            print(f"❌ Error processing files for output '{output_name}': {e}")
            return False

    return True


def verify_local_files(file_object):
    """
    Verify that all required local files exist.

    Args:
        file_object: A dictionary containing file paths to verify.

    Returns:
        bool: True if all files exist, False otherwise.
    """
    try:
        # Get the paths dictionary
        paths = file_object["paths"]
        required_files = [
            f"{LOCAL_DIR}/{file_path}" for file_path in paths.values() if file_path  # Only include non-None paths
        ]

        for file in required_files:
            if not os.path.exists(file):
                print(f"❌ Missing required file: {file}")
                return False

        print("✅ All required local files are present.")
        return True
    except Exception as e:
        print(f"❌ Error verifying local files: {e}")
        return False


def get_input_by_name(cfg, input_name):
    """Get input by name from the resolved configuration."""
    for input_item in cfg.get("inputs", []):
        if input_item.get("name") == input_name:
            return input_item
    return None


def get_output_by_name(cfg, output_name):
    """Get output by name from the resolved configuration."""
    for output_item in cfg.get("outputs", []):
        if output_item.get("name") == output_name:
            return output_item
    return None


def main(cfg):
    """Main function to run RasUnsteady."""
    env, ras_exe_path = setup_environment()

    model_files = get_input_by_name(cfg, "ras_model_files")
    if not model_files:
        print("❌ Error: 'ras_model_files' input not found in configuration.")
        return 1

    local_tmp_hdf = f"{LOCAL_DIR}/{model_files['paths']['tmp_hdf']}"
    local_root = Path(local_tmp_hdf).parent

    attrs = cfg["attributes"]

    # Process inputs
    inputs = [input_item["name"] for input_item in cfg.get("inputs", [])]
    for input_name in inputs:
        files = get_input_by_name(cfg, input_name)
        if not files:
            print(f"❌ Error: Input '{input_name}' not found.")
            return 1

        if files["store_type"] == "S3":
            files_verified = download_s3_input(cfg, [input_name])
        elif files["store_type"] == "FS":
            files_verified = verify_local_files(files)
        else:
            print(f"❌ Unsupported store type: {files['store_type']}")
            return 1

        if not files_verified:
            print(f"❌ Error processing input: {input_name}")
            return 1

    # Run RasUnsteady
    success_phrase = "Finished Unsteady Flow Simulation"
    cmd = [f"{ras_exe_path}/RasUnsteady", local_tmp_hdf, f"x{attrs['geom']}"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, text=True, bufsize=1)
    found_success = False

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
        print("❌ Interrupted.")
        return 2

    if not found_success or proc.returncode != 0:
        print("❌ Error: RasUnsteady failed.")
        return 2

    # Process outputs
    outputs = [output_item["name"] for output_item in cfg.get("outputs", [])]
    subprocess.call(["cp", local_tmp_hdf, local_tmp_hdf.replace(".tmp.hdf", ".hdf")])
    for output_name in outputs:
        output = get_output_by_name(cfg, output_name)
        if not output:
            print(f"❌ Error: Output '{output_name}' not found.")
            return 1

        if output["store_type"] == "S3":
            files_verified = process_output_files(cfg, [output_name], local_source=local_root, action="upload")
        elif output["store_type"] == "FS":
            destination_dir = LOCAL_OUTPUT_DIR
            files_verified = process_output_files(
                cfg, [output_name], local_source=local_root, action="copy", destination_dir=destination_dir
            )
        else:
            print(f"❌ Unsupported store type: {output['store_type']}")
            return 1

        if not files_verified:
            print(f"❌ Error processing output: {output_name}")
            return 1

    print("✅ RasUnsteady succeeded!")
    return 0


if __name__ == "__main__":
    # Get the JSON configuration from command line arguments
    config_json = "".join(sys.argv[1:])

    # Use the resolve-config binary to parse and resolve the configuration
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
        print(f"❌ Unexpected error during configuration resolution: {e}", file=sys.stderr)
        sys.exit(1)

    # print("✅ Configuration resolved successfully.")
    # print(json.dumps(resolved_config, indent=2))

    exit_code = main(resolved_config)
    sys.exit(exit_code)
