#!/bin/bash
# Backup Clojure project with timestamped directory

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <project_dir> <backup_dir>"
    exit 1
fi

PROJECT_DIR=$1
BACKUP_DIR=$2

# Create timestamped backup directory
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_PATH="$BACKUP_DIR/clojure_backup_$TIMESTAMP"

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    echo "Error: Project directory $PROJECT_DIR does not exist."
    exit 1
fi

# Create backup directory
mkdir -p "$BACKUP_PATH"

# Copy project files
rsync -a --exclude='.git' --exclude='target/' "$PROJECT_DIR/" "$BACKUP_PATH/"

# Check rsync result
if [ $? -eq 0 ]; then
    echo "Backup completed successfully to $BACKUP_PATH"
else
    echo "Backup failed."
    exit 1
fi