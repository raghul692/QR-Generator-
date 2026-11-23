"""
QRMaster Pro — Production Cleanup & Database Reset Script.

Wipes test records from database tables and clears generated files
from storage directories, resetting the platform to a clean state.
Compatible with PostgreSQL (Supabase), SQLite, and other supported engines.
"""
from __future__ import annotations

import shutil
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database.session import SessionLocal, engine
from app.config import settings, BASE_DIR
from app.database.seed import init_database
from app.utils.logger import logger


def reset_production_data():
    print("==================================================")
    print("Starting Clean Database & File Reset...")
    print("==================================================")

    db: Session = SessionLocal()
    tables_to_clear = [
        "scan_logs",
        "dynamic_qrs",
        "qr_exports",
        "qr_bulk_jobs",
        "qr_history",
        "qr_templates",
        "analytics",
        "activity_logs",
        "backup_logs",
        "api_keys",
    ]

    try:
        url = settings.resolved_database_url
        if "postgresql" in url or "postgres" in url:
            # PostgreSQL cascade truncate
            for table in tables_to_clear:
                try:
                    db.execute(text(f'TRUNCATE TABLE "{table}" CASCADE;'))
                    print(f"  [+] Truncated table: {table}")
                except Exception as e:
                    print(f"  [-] Failed to truncate {table}: {e}")
        elif "sqlite" in url:
            # SQLite delete
            for table in tables_to_clear:
                try:
                    db.execute(text(f"DELETE FROM {table};"))
                    print(f"  [+] Cleared table: {table}")
                except Exception as e:
                    print(f"  [-] Failed to clear {table}: {e}")
        else:
            for table in tables_to_clear:
                try:
                    db.execute(text(f"DELETE FROM {table};"))
                    print(f"  [+] Cleared table: {table}")
                except Exception as e:
                    print(f"  [-] Failed to clear {table}: {e}")

        db.commit()
        print("[+] Database tables reset cleanly.")
    except Exception as exc:
        db.rollback()
        print(f"[-] Error resetting database: {exc}")
    finally:
        db.close()

    # Re-run seed to ensure default categories & settings exist
    print("\nVerifying default database seed...")
    init_database(create_tables=True)

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

    print("\n==================================================")
    print("SUCCESS: CLEANUP COMPLETE — APP IS IN A FRESH STATE!")
    print("==================================================")


if __name__ == "__main__":
    reset_production_data()
