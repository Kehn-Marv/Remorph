#!/usr/bin/env python3
"""
Maintenance utilities for Remorph fingerprint database and system health.
"""

import json
import os
import argparse
from datetime import datetime
from typing import Dict, Any

from src.config import FINGERPRINTS_PATH, OUTPUT_DIR
from src.trace.attribution import AttributionIndex
from src.utils.logging import setup_logger

logger = setup_logger(__name__)

def cleanup_old_outputs(days_old: int = 7):
    """Remove output files older than specified days"""
    import time
    
    if not os.path.exists(OUTPUT_DIR):
        logger.info("Output directory doesn't exist")
        return
    
    cutoff_time = time.time() - (days_old * 24 * 60 * 60)
    removed_count = 0
    
    for filename in os.listdir(OUTPUT_DIR):
        filepath = os.path.join(OUTPUT_DIR, filename)
        if os.path.isfile(filepath):
            if os.path.getmtime(filepath) < cutoff_time:
                try:
                    os.remove(filepath)
                    removed_count += 1
                    logger.debug(f"Removed old file: {filename}")
                except Exception as e:
                    logger.error(f"Failed to remove {filename}: {e}")
    
    logger.info(f"Cleanup complete: removed {removed_count} files older than {days_old} days")

def backup_fingerprints():
    """Create backup of fingerprints database"""
    if not os.path.exists(FINGERPRINTS_PATH):
        logger.warning("Fingerprints file doesn't exist, nothing to backup")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{FINGERPRINTS_PATH}.backup_{timestamp}"
    
    try:
        import shutil
        shutil.copy2(FINGERPRINTS_PATH, backup_path)
        logger.info(f"Fingerprints backed up to: {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        return None

def validate_fingerprints():
    """Validate fingerprints database integrity"""
    try:
        idx = AttributionIndex(FINGERPRINTS_PATH)
        stats = idx.get_family_stats()
        
        logger.info("Fingerprints validation:")
        logger.info(f"  Total families: {stats['total_families']}")
        logger.info(f"  Total samples: {stats['total_samples']}")
        
        for family in stats['families']:
            logger.info(f"  - {family['name']}: {family['sample_count']} samples")
        
        return True
        
    except Exception as e:
        logger.error(f"Fingerprints validation failed: {e}")
        return False

def reset_fingerprints():
    """Reset fingerprints to default state"""
    backup_path = backup_fingerprints()
    if backup_path:
        logger.info(f"Created backup before reset: {backup_path}")
    
    try:
        if os.path.exists(FINGERPRINTS_PATH):
            os.remove(FINGERPRINTS_PATH)
        
        # This will trigger creation of default database
        idx = AttributionIndex(FINGERPRINTS_PATH)
        logger.info("Fingerprints database reset to defaults")
        
    except Exception as e:
        logger.error(f"Reset failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="Remorph maintenance utilities")
    parser.add_argument("command", choices=["cleanup", "backup", "validate", "reset"])
    parser.add_argument("--days", type=int, default=7, help="Days for cleanup (default: 7)")
    
    args = parser.parse_args()
    
    if args.command == "cleanup":
        cleanup_old_outputs(args.days)
    elif args.command == "backup":
        backup_fingerprints()
    elif args.command == "validate":
        validate_fingerprints()
    elif args.command == "reset":
        reset_fingerprints()

if __name__ == "__main__":
    main()