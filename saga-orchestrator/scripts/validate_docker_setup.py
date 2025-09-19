#!/usr/bin/env python3
"""
Validate Docker setup without actually building
"""

import os
import sys
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a file exists"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description} missing: {file_path}")
        return False

def validate_docker_setup():
    """Validate all required files for Docker build"""
    print("🔍 Validating Docker setup...")
    print("=" * 40)
    
    base_dir = Path(__file__).parent.parent
    
    checks = [
        (base_dir / "Dockerfile", "Dockerfile"),
        (base_dir / "pyproject.toml", "Project configuration"),
        (base_dir / "uv.lock", "UV lock file"),
        (base_dir / "README.md", "README file"),
        (base_dir / "app.py", "Main application"),
        (base_dir / "src", "Source directory"),
        (base_dir / ".dockerignore", "Docker ignore file"),
    ]
    
    all_good = True
    for file_path, description in checks:
        if not check_file_exists(file_path, description):
            all_good = False
    
    print("\n" + "=" * 40)
    
    if all_good:
        print("✅ All required files present for Docker build")
        print("\n🐳 Ready to build with:")
        print("   docker build -t saga-orchestrator .")
        print("\n🚀 Or use make commands:")
        print("   make simple-up    # Build and start everything")
        print("   make dev-up       # Start infrastructure only")
        return True
    else:
        print("❌ Some required files are missing")
        print("Please ensure all files are present before building")
        return False

def check_docker_compose_files():
    """Check Docker Compose files"""
    print("\n🐳 Checking Docker Compose files...")
    
    base_dir = Path(__file__).parent.parent
    
    compose_files = [
        (base_dir / "docker-compose.yml", "Full environment"),
        (base_dir / "docker-compose.dev.yml", "Development environment"),
        (base_dir / "docker-compose.simple.yml", "Simple environment"),
    ]
    
    for file_path, description in compose_files:
        check_file_exists(file_path, f"{description} compose file")

def main():
    """Main validation function"""
    print("🧪 Docker Setup Validation")
    print("=" * 40)
    
    setup_valid = validate_docker_setup()
    check_docker_compose_files()
    
    print("\n" + "=" * 40)
    print("📋 Next Steps:")
    
    if setup_valid:
        print("1. Build the Docker image:")
        print("   docker build -t saga-orchestrator .")
        print("\n2. Or start with infrastructure:")
        print("   make dev-up")
        print("   make run")
        print("\n3. Or start everything:")
        print("   make simple-up")
        
        return 0
    else:
        print("1. Fix missing files")
        print("2. Run this script again")
        print("3. Then try building")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
