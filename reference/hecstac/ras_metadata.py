#!/usr/bin/env python3
from hecstac.common.logger import initialize_logger
from hecstac.ras.item import RASModelItem
import logging
import sys

def usage():
    print("Usage:")
    print("  ras_metadata <ras_project_file> <item_id> <crs (optional)>")
    print("  example: ras_metadata /mnt/Muncie.prj muncie")
    sys.exit(1)


def run_one(ras_project_file, item_id, crs=None):
    try:
        ras_item = RASModelItem.from_prj(ras_project_file, crs=crs)
        ras_item.save_object(ras_item.pm.item_path(item_id))
        logging.info(f"✅ Processed {ras_project_file} → {ras_item.pm.item_path(item_id)}")
    except Exception as e:
        logging.info(f"❌ Processing failed: {ras_project_file} → {item_id}")
        logging.info(f"Reason: {str(e)}")
        sys.exit(1)

def main():
    initialize_logger()
    logging.info("Starting RAS metadata processing...")
    if len(sys.argv) == 4:
        ras_project_file = sys.argv[1]
        item_id = sys.argv[2]
        crs= sys.argv[3]
        run_one(ras_project_file, item_id,crs)

    elif len(sys.argv) == 3:
        ras_project_file = sys.argv[1]
        item_id = sys.argv[2]
        run_one(ras_project_file, item_id)

    else:
        usage()

if __name__ == "__main__":
    main()


