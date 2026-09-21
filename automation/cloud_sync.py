import os
import sys
import shutil
import datetime
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from core.paths import paths
from core.config import ApexGhostConfig

def perform_cloud_sync() -> bool:
    """
    Archives the local database and uploads it to AWS S3.
    Requires AWS credentials to be configured (e.g., via `aws configure`).
    Returns True if successful, False otherwise.
    """
    config = ApexGhostConfig.load()
    if not config.cloud_backup.enable_aws_sync:
        print("[Cloud Sync] AWS Backup is disabled in config.")
        return False

    bucket_name = config.cloud_backup.aws_bucket_name
    region = config.cloud_backup.aws_region

    if not bucket_name or bucket_name == "apex-ghost-backup-bucket":
        print("[Cloud Sync] Please configure a valid AWS bucket name in core/apex_ghost_config.json")
        return False

    try:
        import boto3
        from botocore.exceptions import ClientError
    except ImportError:
        print("[Cloud Sync] boto3 is not installed. Please run `pip install boto3`.")
        return False

    # 1. Create temporary archive
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"apex_ghost_backup_{timestamp}"
    archive_path = paths.core_dir / "backups"
    archive_path.mkdir(exist_ok=True)
    
    zip_target = archive_path / archive_name
    db_path = paths.storage_dir / "apex_ghost.db"

    if not db_path.exists():
        print(f"[Cloud Sync] Database not found at {db_path}. Nothing to sync.")
        return False

    print(f"[Cloud Sync] Compressing {db_path} to {zip_target}.zip...")
    
    # We copy the db file to a temp directory to zip it cleanly
    temp_dir = archive_path / "temp_backup"
    temp_dir.mkdir(exist_ok=True)
    try:
        shutil.copy2(db_path, temp_dir / "apex_ghost.db")
        shutil.make_archive(str(zip_target), 'zip', str(temp_dir))
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    zip_file = f"{zip_target}.zip"

    # 2. Upload to S3
    print(f"[Cloud Sync] Uploading {archive_name}.zip to s3://{bucket_name}...")
    s3_client = boto3.client('s3', region_name=region)
    try:
        s3_client.upload_file(zip_file, bucket_name, f"{archive_name}.zip")
        print("[Cloud Sync] Upload complete!")
    except ClientError as e:
        print(f"[Cloud Sync] AWS S3 Upload Failed: {e}")
        return False

    # 3. Cleanup local zip (optional, keeping last 5 could be good)
    # We'll keep it locally as well for double redundancy, but let's prune old ones
    try:
        backups = sorted(archive_path.glob("*.zip"))
        if len(backups) > 7:
            for old_backup in backups[:-7]:
                old_backup.unlink()
    except Exception as e:
        print(f"[Cloud Sync] Cleanup error: {e}")

    return True

if __name__ == "__main__":
    perform_cloud_sync()
