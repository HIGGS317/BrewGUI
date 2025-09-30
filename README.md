# Homebrew GUI

## Description

This application is an easy-to-use GUI for the Homebrew package manager on macOS. It supports basic Homebrew commands such as install, uninstall, search, and update.

## Features

- Lists all installed Homebrew packages, including both command-line formulae and GUI casks.
- Switches between filtering your installed packages and searching all of Homebrew for new ones.
- Installs, uninstalls, and upgrades packages.
- A responsive interface that doesn't freeze during long operations.

## Requirements

- macOS
- Python 3
- Homebrew
- PySide6 (`pip install PySide6`)

## How to Run

Navigate to the project's directory in your terminal and run the script:

```bash
python brew_gui.py
```

## Building the Application (Optional)

1. Install pyinstaller

```bash
pip install pyinstaller
```

2. Run the build command from project directory

```bash
pyinstaller --noconsole --onefile --name "Brew GUI" brew_gui.py
```

The final application will be in dist folder and is searchable through spotlight and can be run as a normal GUI app
