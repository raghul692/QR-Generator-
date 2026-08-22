"""
QRMaster Pro — Production Cleanup & Database Reset Script.

Wipes all test records from database tables and clears all generated files
from storage directories, resetting the platform to a 100% fresh, production-ready state.
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database.session import SessionLocal, engine
from app.config import settings, BASE_DIR
from app.database.seed import init_database


def reset_production_data():
    print("==================================================")
    print("Starting Production Data Cleanup & Reset...")
    print("==================================================")

    db: Session = SessionLocal()
    try:
        # Disable foreign key checks for clean truncation
        db.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        
        tables_to_truncate = [
            "qr_history",
            "qr_exports",
            "qr_bulk_jobs",
            "analytics",
            "activity_logs",
            "backup_logs",
            "dynamic_qrs",
            "scan_logs",
            "api_keys",
        ]

        for table in tables_to_truncate:
            try:
                db.execute(text(f"TRUNCATE TABLE {table};"))
                print(f"  [+] Truncated table: {table}")
            except Exception as e:
                print(f"  [-] Failed to truncate {table}: {e}")

        # Re-enable foreign key checks
        db.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
        db.commit()
        print("[+] Database tables reset cleanly.")

    except Exception as exc:
        db.rollback()
        print(f"[-] Error resetting database: {exc}")
    finally:
        db.close()

    # Re-run seed to ensure default categories & settings exist
    print("\nVerifying default database seed...")
    init_database()

    # Clean storage directories
    storage_dirs = [
        settings.generated_qr_path,
        settings.uploads_path,
        settings.exports_path,
        settings.logs_path,
        settings.backup_path,
    ]

    print("\nCleaning up physical file storage...")
    for s_dir in storage_dirs:
        if s_dir.exists():
            for item in s_dir.iterdir():
                try:
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                    print(f"  [+] Deleted: {item.name}")
                except Exception as err:
                    print(f"  [-] Could not delete {item.name}: {err}")

    # Remove temporary test scripts
    test_files = [
        BASE_DIR / "test_enterprise_features.py",
        BASE_DIR / "test_settings.py",
    ]
    for tf in test_files:
        if tf.exists():
            tf.unlink()
            print(f"  [+] Removed temporary test file: {tf.name}")

    print("\n==================================================")
    print("SUCCESS: PRODUCTION CLEANUP COMPLETE — APP IS 100% FRESH!")
    print("==================================================")


if __name__ == "__main__":
    reset_production_data()
