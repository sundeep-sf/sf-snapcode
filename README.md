# snapcode

A simple utility to create and maintain snapshots of your codebase. It watches for file changes and automatically creates a snapshot when files are modified.

## Features

- Creates snapshots of all text-based code files (automatically detected)
- skips binary files
- excludes common development directories (`.git`, `.venv`, etc.)
- watches for file changes and updates snapshots in real-time
- cooldown to prevent excessive snapshot creation

## Installation

```bash
pipx install git+https://github.com/sundeep-sf/sf-snapcode.git
```

## Usage

Run in current directory:
```bash
snapcode
```

Run in specific directory:
```bash
snapcode /path/to/project
```

The tool will:
1. Create an initial snapshot
2. Start watching for changes
3. Show real-time updates when files change:
   ```
   Creating initial snapshot in: /current/path
   Added: src/main.py
   Added: README.md
   Added: src/lib.py
   
   Processed 4 files successfully!
   
   Starting file watcher...
   Watching for changes. Press Ctrl+C to stop...
   
   File change detected: src/main.py
   ```
