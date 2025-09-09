import subprocess
import os
import platform

def find_llama_cpp_binary():
    """
    Searches for the llama.cpp 'main' binary in common locations.
    """
    system = platform.system()
    binary_name = "main"
    if system == "Windows":
        binary_name += ".exe"

    # Paths to check, relative to this script's location (Core/utils)
    script_dir = os.path.dirname(__file__)
    search_paths = [
        os.path.join(script_dir, '..', binary_name),  # ../Core/main
        os.path.join(script_dir, '..', '..', 'llama.cpp', binary_name), # ../llama.cpp/main
    ]

    # Check each path
    for path in search_paths:
        if os.path.exists(path) and os.access(path, os.X_OK):
            return os.path.abspath(path)

    # Fallback: check system PATH
    from shutil import which
    if which(binary_name):
        return which(binary_name)
        
    return None

def run_inference(model_path, prompt):
    """
    Runs the llama.cpp binary with a given model and prompt.
    """
    binary_path = find_llama_cpp_binary()
    if not binary_path:
        print("ERROR: llama.cpp binary not found.")
        print("Please build it and place it in 'Core/' or ensure it's in your system's PATH.")
        return "Error: llama.cpp binary not found."

    if not os.path.exists(model_path):
        print(f"ERROR: Model file not found at '{model_path}'.")
        return f"Error: Model not found at '{model_path}'."

    # Standard parameters for llama.cpp
    params = {
        "model": model_path,
        "prompt": prompt,
        "n-predict": 1024,  # Max tokens to generate
        "ctx-size": 4096,
        "temp": 0.7,
        "top-p": 0.9,
    }

    # Construct the command
    command = [binary_path]
    for key, value in params.items():
        command.extend([f"--{key}", str(value)])

    print(f"\nExecuting Llama.cpp: {' '.join(command)}\n")

    try:
        # Execute the command
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except FileNotFoundError:
        return "Error: The 'main' executable was not found at the specified path."
    except subprocess.CalledProcessError as e:
        error_message = f"Llama.cpp execution failed with exit code {e.returncode}.\n"
        error_message += f"Stderr:\n{e.stderr}"
        return error_message

if __name__ == '__main__':
    # Example usage for testing
    print("--- Llama Runner Test ---")
    binary = find_llama_cpp_binary()
    if binary:
        print(f"Found llama.cpp binary at: {binary}")
        # This part requires a model to be present for a full test.
        # We'll just simulate the check.
        print("To run a full test, place a GGUF model in the Models/ directory.")
        print("Example: Models/dolphin-2.9-mistral-7b.Q4_K_M.gguf")
    else:
        print("Llama.cpp binary not found. Please follow README instructions.")
