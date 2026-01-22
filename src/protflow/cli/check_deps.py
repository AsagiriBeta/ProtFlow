#!/usr/bin/env python3
"""
Utility script to check system dependencies for ProtFlow.
"""
import shutil
import subprocess
import sys
from pathlib import Path


def check_command(cmd: str, name: str, required: bool = True) -> bool:
    """Check if a command is available."""
    available = shutil.which(cmd) is not None
    status = "✓" if available else "✗"
    req = "REQUIRED" if required else "OPTIONAL"
    print(f"{status} {name:20s} [{req}] - {cmd}")
    return available


def check_java_version():
    """Check Java version."""
    try:
        result = subprocess.run(
            ["java", "-version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        version_line = result.stderr.split('\n')[0]
        print(f"  Java version: {version_line}")
        return True
    except Exception:
        return False


def check_python_packages():
    """Check Python packages."""
    packages = [
        ("esm", True),
        ("Bio", True),  # biopython
        ("pandas", True),
        ("torch", True),
        ("reportlab", True),
        ("tqdm", True),
        ("matplotlib", False),
        ("pytest", False),
    ]

    print("\nPython Packages:")
    all_good = True
    for pkg, required in packages:
        try:
            __import__(pkg)
            status = "✓"
        except ImportError:
            status = "✗"
            if required:
                all_good = False
        req = "REQUIRED" if required else "OPTIONAL"
        print(f"{status} {pkg:20s} [{req}]")

    return all_good


def main():
    """Main check function."""
    print("=" * 60)
    print("ProtFlow Dependency Check")
    print("=" * 60)

    print("\nSystem Commands:")
    java_ok = check_command("java", "Java (for P2Rank)", required=True)
    if java_ok:
        check_java_version()

    obabel_ok = check_command("obabel", "OpenBabel", required=True)
    vina_ok = check_command("vina", "AutoDock Vina", required=True)
    check_command("wget", "wget", required=False)
    check_command("curl", "curl", required=False)

    pkg_ok = check_python_packages()

    print("\n" + "=" * 60)

    required_ok = java_ok and obabel_ok and vina_ok and pkg_ok

    if required_ok:
        print("✓ All required dependencies are installed!")
        print("\nYou can now run:")
        print("  python -m scripts.runner --help")
        return 0
    else:
        print("✗ Some required dependencies are missing.")
        print("\nPlease install missing dependencies:")

        if sys.platform == "darwin":
            print("\nFor macOS, run:")
            print("  bash scripts/setup_macos.sh")
            print("  pip install -r requirements.txt")
        elif sys.platform.startswith("linux"):
            print("\nFor Ubuntu/Debian, run:")
            print("  bash scripts/setup_ubuntu.sh")
            print("  pip install -r requirements.txt")
        else:
            print("\nPlease install:")
            if not java_ok:
                print("  - Java (JRE)")
            if not obabel_ok:
                print("  - OpenBabel")
            if not vina_ok:
                print("  - AutoDock Vina")
            if not pkg_ok:
                print("  - Python packages: pip install -r requirements.txt")

        return 1


if __name__ == "__main__":
    sys.exit(main())

