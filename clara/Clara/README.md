# Clara Academic Assistant
**Portable, encrypted, offline study optimization**

Clara is a 100% local, offline-first AI assistant designed for serious academic work. It runs on your own hardware, ensuring your study materials and data remain private. It is designed to be run from a portable, encrypted drive like a VeraCrypt volume.

## VeraCrypt Setup (Recommended)
For maximum privacy, run Clara from within an encrypted VeraCrypt container.

1.  **Create Container**:
    *   Size: 90-100GB (to hold models and documents)
    *   Encryption: `AES(Twofish)` or `Serpent(AES)`
    *   Hash: `SHA-512`
    *   Filesystem: `exFAT` (for cross-platform compatibility)
2.  **Mount Volume**: Mount the created VeraCrypt volume to a drive letter or mount point.

## Installation

1.  **Place Clara**: Copy the entire `Clara` project folder into your mounted VeraCrypt volume.

2.  **Install Dependencies**:
    ```bash
    # Navigate to the Clara directory
    cd /path/to/mounted/volume/Clara

    # Install Python packages
    pip install -r requirements.txt
    ```

3.  **Build `llama.cpp`**: Clara uses `llama.cpp` for local model inference.
    ```bash
    # Clone the repository
    git clone https://github.com/ggerganov/llama.cpp
    
    # Build it (this may vary based on your system, e.g., with CUDA/Metal support)
    cd llama.cpp
    make -j8
    
    # Copy the main executable to a location Clara can find
    # This makes it portable with the Clara folder.
    cp main ../Clara/Core/
    cd ..
    ```

4.  **Download Models**: Download GGUF-quantized language models and place them in the `Clara/Models/` directory. The default policy uses:
    *   `dolphin-2.9-mistral-7b.Q4_K_M.gguf`
    *   `openhermes-2.5-mistral-7b.Q4_K_M.gguf`
    *   `llama-3-8b-instruct.Q4_K_M.gguf`

## Usage

1.  **Make Launchers Executable** (macOS / Linux):
    ```bash
    chmod +x Launchers/LaunchClara.command
    chmod +x Launchers/LaunchClara.sh
    ```

2.  **Start Clara**: Run the appropriate launcher for your operating system from the `Launchers` directory.
    *   macOS: `./Launchers/LaunchClara.command`
    *   Linux: `./Launchers/LaunchClara.sh`
    *   Windows: Double-click `LaunchClara.bat`

## Commands
Once Clara is running, you can use the following commands:

*   `predict <subject>`: Forecasts likely exam topics based on your materials in the `Docs/` folder.
*   `schedule`: Creates a study plan based on your inputs.
*   `organize`: Helps create outlines, summaries, or flashcards from your documents.
*   `help`: Shows the list of available commands.
*   `exit` or `quit`: Closes the application.

## Security
- **100% Offline**: Clara performs no network calls.
- **Encrypted**: Designed to run within a VeraCrypt container.
- **Private**: Your data never leaves your machine.
