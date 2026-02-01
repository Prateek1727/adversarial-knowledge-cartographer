"""Verification script to check project setup is complete."""

import os
import sys
from pathlib import Path


def check_file_exists(filepath: str, description: str) -> bool:
    """Check if a file exists and report status."""
    exists = Path(filepath).exists()
    status = "✓" if exists else "✗"
    print(f"{status} {description}: {filepath}")
    return exists


def check_directory_exists(dirpath: str, description: str) -> bool:
    """Check if a directory exists and report status."""
    exists = Path(dirpath).is_dir()
    status = "✓" if exists else "✗"
    print(f"{status} {description}: {dirpath}")
    return exists


def main():
    """Run verification checks."""
    print("=" * 60)
    print("Adversarial Knowledge Cartographer - Setup Verification")
    print("=" * 60)
    print()
    
    all_checks = []
    
    # Check directories
    print("Checking directories...")
    all_checks.append(check_directory_exists("agents", "Agents module"))
    all_checks.append(check_directory_exists("models", "Models module"))
    all_checks.append(check_directory_exists("utils", "Utils module"))
    all_checks.append(check_directory_exists("tests", "Tests module"))
    print()
    
    # Check core files
    print("Checking core files...")
    all_checks.append(check_file_exists("config.py", "Configuration module"))
    all_checks.append(check_file_exists("main.py", "Main entry point"))
    all_checks.append(check_file_exists("requirements.txt", "Dependencies file"))
    all_checks.append(check_file_exists("setup.py", "Setup script"))
    print()
    
    # Check configuration files
    print("Checking configuration files...")
    all_checks.append(check_file_exists(".env.example", "Environment template"))
    all_checks.append(check_file_exists(".gitignore", "Git ignore file"))
    all_checks.append(check_file_exists("pytest.ini", "Pytest config"))
    print()
    
    # Check documentation
    print("Checking documentation...")
    all_checks.append(check_file_exists("README.md", "Main README"))
    all_checks.append(check_file_exists("QUICKSTART.md", "Quick start guide"))
    all_checks.append(check_file_exists("PROJECT_STRUCTURE.md", "Structure docs"))
    print()
    
    # Check setup scripts
    print("Checking setup scripts...")
    all_checks.append(check_file_exists("setup.bat", "Windows setup script"))
    all_checks.append(check_file_exists("setup.sh", "Unix setup script"))
    print()
    
    # Check tests
    print("Checking tests...")
    all_checks.append(check_file_exists("tests/test_config.py", "Config tests"))
    print()
    
    # Check spec files
    print("Checking spec files...")
    all_checks.append(check_file_exists(
        ".kiro/specs/adversarial-knowledge-cartographer/requirements.md",
        "Requirements doc"
    ))
    all_checks.append(check_file_exists(
        ".kiro/specs/adversarial-knowledge-cartographer/design.md",
        "Design doc"
    ))
    all_checks.append(check_file_exists(
        ".kiro/specs/adversarial-knowledge-cartographer/tasks.md",
        "Tasks doc"
    ))
    print()
    
    # Try importing config
    print("Checking Python imports...")
    try:
        from config import Config
        print("✓ Config module imports successfully")
        all_checks.append(True)
    except Exception as e:
        print(f"✗ Config module import failed: {e}")
        all_checks.append(False)
    print()
    
    # Check for .env file
    print("Checking environment configuration...")
    if Path(".env").exists():
        print("✓ .env file exists")
        print("  Note: Make sure you've added your API keys!")
    else:
        print("✗ .env file not found")
        print("  Action required: Copy .env.example to .env and add your API keys")
    print()
    
    # Check for virtual environment
    print("Checking virtual environment...")
    if Path("venv").exists():
        print("✓ Virtual environment exists")
    else:
        print("✗ Virtual environment not found")
        print("  Action required: Run setup.bat (Windows) or setup.sh (Unix)")
    print()
    
    # Summary
    print("=" * 60)
    passed = sum(all_checks)
    total = len(all_checks)
    print(f"Setup verification: {passed}/{total} checks passed")
    
    if passed == total:
        print("✓ Project setup is complete!")
        print()
        print("Next steps:")
        print("1. Create .env file from .env.example and add API keys")
        print("2. Run setup.bat (Windows) or setup.sh (Unix) to install dependencies")
        print("3. Run 'pytest tests/test_config.py' to verify installation")
        print("4. Start implementing tasks from tasks.md")
        return 0
    else:
        print("✗ Some checks failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
