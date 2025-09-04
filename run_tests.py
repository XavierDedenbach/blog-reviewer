#!/usr/bin/env python3
import subprocess
import sys

def main():
    # Install pytest if not available
    try:
        import pytest
    except ImportError:
        print("Installing pytest...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pytest>=7.0.0", "pytest-asyncio>=0.21.0", "pytest-mock>=3.10.0"])
    
    # Run tests
    import pytest
    return pytest.main(["-v", "tests/"])

if __name__ == "__main__":
    sys.exit(main())