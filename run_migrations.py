"""
Run all database migrations
"""
import subprocess
import sys

def run_migration(script_name):
    """Run a migration script"""
    print(f"\n{'='*60}")
    print(f"Running: {script_name}")
    print('='*60)
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        if result.stderr:
            print("Warnings:", result.stderr)
        print(f"✓ {script_name} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {script_name} failed:")
        print(e.stdout)
        print(e.stderr)
        return False

def main():
    """Run all migrations"""
    print("\n" + "="*60)
    print("JOBNECT DATABASE MIGRATIONS")
    print("="*60)
    
    migrations = [
        'add_skills_column.py',
        'add_designation_city_columns.py',
    ]
    
    success_count = 0
    failed_count = 0
    
    for migration in migrations:
        if run_migration(migration):
            success_count += 1
        else:
            failed_count += 1
    
    print("\n" + "="*60)
    print("MIGRATION SUMMARY")
    print("="*60)
    print(f"✓ Successful: {success_count}")
    print(f"✗ Failed: {failed_count}")
    print("="*60)
    
    if failed_count > 0:
        print("\n⚠️  Some migrations failed. Please check the errors above.")
        sys.exit(1)
    else:
        print("\n✓ All migrations completed successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()
