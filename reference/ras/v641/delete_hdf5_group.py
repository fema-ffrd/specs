"""
Delete a group (and its contents) from an HDF5 file.

Example:
  python3 delete_hdf5_group.py /path/to/file.hdf5 --group results --backup --yes
"""
import argparse
import os
import sys

import h5py

def main():
    p = argparse.ArgumentParser(description="Delete an HDF5 group (recursively).")
    p.add_argument("file", help="Path to HDF5 file")
    p.add_argument("--group", "-g", default="Results", help="Group name to delete (default: results)")
    args = p.parse_args()

    fp = os.path.expanduser(args.file)
    if not os.path.isfile(fp):
        print(f"Error: file not found: {fp}", file=sys.stderr)
        sys.exit(2)

    grp_key = args.group.lstrip("/")

    try:
        with h5py.File(fp, "r+") as f:
            if grp_key in f:
                del f[grp_key]
                # ensure changes flushed
                f.flush()
                print(f"Deleted group '/{grp_key}' from {fp}")
            else:
                print(f"Group '/{grp_key}' not found in {fp}", file=sys.stderr)
                sys.exit(1)
    except Exception as e:
        print(f"Error modifying HDF5 file: {e}", file=sys.stderr)
        sys.exit(4)

if __name__ == "__main__":
    main()