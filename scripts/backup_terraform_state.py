import os
import shutil
from datetime import datetime

def backup_terraform_state(terraform_state_path, backup_dir):
    """Backs up Terraform state files to a specified backup directory."""
    
    # Ensure backup directory exists
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    # Get current timestamp for backup filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Determine filename
    base_name = os.path.basename(terraform_state_path)
    file_name = f"{os.path.splitext(base_name)[0]}_{timestamp}.tfstate"
    backup_path = os.path.join(backup_dir, file_name)

    # Perform backup
    try:
        shutil.copy2(terraform_state_path, backup_path)
        print(f"Backup created at {backup_path}")
    except Exception as e:
        print(f"Failed to backup Terraform state: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: backup_terraform_state.py <terraform_state_path> <backup_dir>")
        sys.exit(1)

    terraform_state_path = sys.argv[1]
    backup_dir = sys.argv[2]

    backup_terraform_state(terraform_state_path, backup_dir)