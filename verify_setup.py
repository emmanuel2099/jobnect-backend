#!/usr/bin/env python3
"""
Verification script to check if all dependencies are installed correctly.
Run this before starting the backend server.
"""

import sys

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need 3.8+")
        return False

def check_dependencies():
    """Check if all required packages are installed"""
    dependencies = [
        ("fastapi", "FastAPI"),
        ("sqlalchemy", "SQLAlchemy"),
        ("pydantic", "Pydantic"),
        ("passlib", "Passlib"),
        ("jose", "Python-JOSE"),
        ("psycopg2", "Psycopg2"),
        ("uvicorn", "Uvicorn"),
    ]
    
    all_ok = True
    for module, name in dependencies:
        try:
            __import__(module)
            print(f"✅ {name} - Installed")
        except ImportError:
            print(f"❌ {name} - Missing")
            all_ok = False
    
    return all_ok

def check_env_file():
    """Check if .env file exists"""
    import os
    if os.path.exists(".env"):
        print("✅ .env file - Found")
        return True
    else:
        print("⚠️  .env file - Not found (copy from .env.example)")
        return False

def check_project_structure():
    """Check if all required files exist"""
    import os
    
    required_files = [
        "main.py",
        "requirements.txt",
        ".env.example",
        "app/__init__.py",
        "app/config.py",
        "app/database.py",
        "app/models.py",
        "app/schemas.py",
        "app/auth.py",
        "app/routers/__init__.py",
        "app/routers/auth.py",
        "app/routers/profile.py",
        "app/routers/jobs.py",
        "app/routers/applications.py",
        "app/routers/companies.py",
        "app/routers/master_data.py",
    ]
    
    all_ok = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - Missing")
            all_ok = False
    
    return all_ok

def main():
    print("=" * 60)
    print("JobNect Backend - Setup Verification")
    print("=" * 60)
    print()
    
    print("1. Checking Python Version...")
    python_ok = check_python_version()
    print()
    
    print("2. Checking Dependencies...")
    deps_ok = check_dependencies()
    print()
    
    print("3. Checking Environment File...")
    env_ok = check_env_file()
    print()
    
    print("4. Checking Project Structure...")
    structure_ok = check_project_structure()
    print()
    
    print("=" * 60)
    if python_ok and deps_ok and structure_ok:
        print("✅ ALL CHECKS PASSED!")
        print()
        print("You can now run the backend:")
        print("  python main.py")
        print()
        if not env_ok:
            print("⚠️  Don't forget to create .env file:")
            print("  cp .env.example .env")
            print("  # Then edit .env with your database credentials")
        print()
        print("API will be available at: http://localhost:8000")
        print("Documentation: http://localhost:8000/docs")
    else:
        print("❌ SOME CHECKS FAILED")
        print()
        if not python_ok:
            print("- Install Python 3.8 or higher")
        if not deps_ok:
            print("- Install dependencies: pip install -r requirements.txt")
        if not structure_ok:
            print("- Some project files are missing")
        if not env_ok:
            print("- Create .env file: cp .env.example .env")
    print("=" * 60)

if __name__ == "__main__":
    main()
