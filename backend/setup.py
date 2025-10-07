import subprocess
import sys

def install_torch():
    print("Installing correct torch version...")
    
    # Uninstall existing torch
    subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", "torch", "torchaudio"])
    
    # Install specific torch version
    torch_command = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "torch==1.10.0+cu102",
        "torchaudio==0.10.0",
        "-f",
        "https://download.pytorch.org/whl/cu102/torch_stable.html"
    ]
    
    try:
        subprocess.check_call(torch_command)
        print("Successfully installed torch 1.10.0+cu102")
    except subprocess.CalledProcessError:
        print("GPU version installation failed, trying CPU version...")
        # Try CPU version if GPU version fails
        subprocess.check_call([
            sys.executable,
            "-m",
            "pip",
            "install",
            "torch==1.10.0",
            "torchaudio==0.10.0"
        ])
        print("Successfully installed torch 1.10.0 (CPU version)")

if __name__ == "__main__":
    install_torch() 