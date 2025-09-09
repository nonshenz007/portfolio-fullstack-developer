# VeriDoc Quickstart Guide

This guide provides instructions on how to set up, run, and use the VeriDoc application.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd VeriDoc
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

To start the VeriDoc graphical user interface, run:

```bash
python main.py
```

## Building the Executable

To build a distributable `.exe` file for Windows, run the build script:

```bash
build_windows.bat
```

The executable will be located in the `.dist/` directory.
