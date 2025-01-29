#!/usr/bin/env python3

import os
import sys
import time
from pathlib import Path
from typing import Set, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


def get_excluded_patterns() -> Set[str]:
    """Return a set of directory and file patterns to exclude from snapshots."""
    return {
        ".git",
        ".idea",
        ".mypy_cache",
        ".ruff_cache",
        ".venv",
        "venv",
        ".pytest_cache",
        "__pycache__",
        ".coverage",
        ".DS_Store",
        ".vscode",
        ".circleci",
        ".github",
        "target",
    }


def is_text_file(file_path: Path) -> bool:
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(1024)
            return b"\x00" not in chunk
    except Exception:
        return False


def should_include_file(file_path: Path, excluded_patterns: Set[str]) -> bool:
    """
    Determine if a file should be included in the snapshot.

    Args:
        file_path: Path to the file to check
        excluded_patterns: Set of patterns to exclude

    Returns:
        bool: True if file should be included, False otherwise
    """
    parts = file_path.parts
    return (
        not any(part in excluded_patterns for part in parts)
        and not file_path.name.startswith(".")
        and is_text_file(file_path)
    )


def create_code_snapshot(project_root: Path, output_file: Optional[str] = None) -> None:
    if output_file is None:
        folder_name = project_root.name
        output_file = f"{folder_name}_snapshot.txt"

    # Convert output_file to full path relative to project_root
    output_path = project_root / output_file

    excluded_patterns = get_excluded_patterns()
    total_files = 0

    with open(output_path, "w", encoding="utf-8") as out:
        for root, dirs, files in os.walk(project_root):
            dirs[:] = [d for d in dirs if d not in excluded_patterns]

            for file in sorted(files):
                file_path = Path(root) / file
                rel_path = file_path.relative_to(project_root)

                if should_include_file(file_path, excluded_patterns):
                    try:
                        out.write(f"\n{'='*80}\n")
                        out.write(f"File: {rel_path}\n")
                        out.write(f"{'='*80}\n\n")

                        with open(file_path, "r", encoding="utf-8") as f:
                            out.write(f.read())

                        total_files += 1
                        print(f"Added: {rel_path}")

                    except Exception as e:
                        print(f"Error processing {file_path}: {str(e)}")

    print(f"\nProcessed {total_files} files successfully!")


class SnapshotHandler(FileSystemEventHandler):
    """
    File system event handler that creates new snapshots when files change.

    Implements a cooldown period to prevent excessive snapshot creation.
    """

    def __init__(self, project_root: Path):
        self.last_snapshot_time = 0
        self.cooldown = 2
        self.excluded_patterns = get_excluded_patterns()
        self.project_root = project_root

    def on_modified(self, event):
        """Handle file modification events by creating a new snapshot if needed."""
        if event.is_directory:
            return

        try:
            file_path = Path(event.src_path)
            rel_path = file_path.relative_to(self.project_root)

            if not should_include_file(file_path, self.excluded_patterns):
                return

            current_time = time.time()
            if current_time - self.last_snapshot_time < self.cooldown:
                return

            print(f"\nFile change detected: {rel_path}")
            create_code_snapshot(self.project_root)
            self.last_snapshot_time = current_time
        except ValueError:
            return


def start_watcher(project_root: Optional[Path] = None) -> None:
    """
    Start watching for file changes and create snapshots.

    Args:
        project_root: Root directory to watch. Defaults to current working directory.
    """
    if project_root is None:
        project_root = Path.cwd()

    print(f"Creating initial snapshot in: {project_root}")
    create_code_snapshot(project_root)

    print("\nStarting file watcher...")
    event_handler = SnapshotHandler(project_root)
    observer = Observer()
    observer.schedule(event_handler, str(project_root), recursive=True)
    observer.start()

    print("Watching for changes. Press Ctrl+C to stop...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nWatcher stopped.")

    observer.join()


def main() -> None:
    """Entry point for the CLI."""
    if len(sys.argv) > 1:
        project_root = Path(sys.argv[1])
    else:
        project_root = None

    start_watcher(project_root)


if __name__ == "__main__":
    main()
