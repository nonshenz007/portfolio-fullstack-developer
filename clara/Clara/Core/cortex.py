import os
import platform
import psutil
import json
import datetime
import subprocess

def detect_hardware():
    """Detects system hardware specifications."""
    system = platform.system()
    arch = platform.machine()
    ram_gb = round(psutil.virtual_memory().total / (1024**3), 2)
    
    gpu = "N/A"
    if system == "Darwin":
        # Rudimentary check for Apple Silicon
        if "arm" in arch.lower():
            gpu = "Apple Silicon (Integrated)"
    elif system == "Linux":
        try:
            gpu_info = subprocess.check_output("lspci | grep -i 'vga|3d|2d'", shell=True, text=True).strip()
            gpu = gpu_info.split(":")[-1].strip()
        except subprocess.CalledProcessError:
            gpu = "N/A (lspci not found or no GPU)"
    elif system == "Windows":
        try:
            gpu_info = subprocess.check_output("wmic path win32_videocontroller get caption", shell=True, text=True).strip().split('\n')[1]
            gpu = gpu_info.strip()
        except Exception:
            gpu = "N/A (wmic not found or no GPU)"

    return {
        "os": system,
        "cpu": arch,
        "ram_gb": ram_gb,
        "gpu": gpu
    }

def get_performance_defaults(ram_gb):
    """Sets performance defaults based on available RAM."""
    if ram_gb <= 8:
        return {"threads": 4, "quant_hint": "Q4_K_M"}
    else:
        return {"threads": 8, "quant_hint": "Q5_K_M"}

def create_runtime_config(hardware, runtime, base_path):
    """Creates and saves the runtime configuration file."""
    config = {
        "generated_at": datetime.datetime.utcnow().isoformat(),
        "hardware": hardware,
        "runtime": runtime,
        "paths": {
            "models": os.path.join(base_path, "Models"),
            "memory": os.path.join(base_path, "Memory")
        }
    }
    config_path = os.path.join(base_path, "Memory", "runtime_config.json")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    return config

def print_banner(config):
    """Prints a startup banner with a hardware summary."""
    print("="*60)
    print("Clara — Portable, Encrypted, Local Study Assistant (offline)")
    print("="*60)
    print("Hardware Summary:")
    print(f"  OS: {config['hardware']['os']}")
    print(f"  CPU: {config['hardware']['cpu']}")
    print(f"  RAM: {config['hardware']['ram_gb']} GB")
    print(f"  GPU: {config['hardware']['gpu']}")
    print("\nRuntime Configuration:")
    print(f"  Threads: {config['runtime']['threads']}")
    print(f"  Quantization Hint: {config['runtime']['quant_hint']}")
    print("\nPaths:")
    print(f"  Models Path: {config['paths']['models']}")
    print(f"  Memory Path: {config['paths']['memory']}")
    print("="*60)

def main():
    """Main function to initialize Clara."""
    # Assuming the script is in Core/, so base path is one level up
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    hardware_info = detect_hardware()
    performance_defaults = get_performance_defaults(hardware_info['ram_gb'])
    config = create_runtime_config(hardware_info, performance_defaults, base_path)
    
    print_banner(config)
    
    # Launch the router REPL
    # Use exec to replace the current process, making it the main loop
    router_path = os.path.join(os.path.dirname(__file__), "router.py")
    os.execlp("python", "python", router_path)

if __name__ == "__main__":
    main()
