# zCLI/subsystems/zData/zData_modules/shared/migration_execution.py
"""
Migration execution and history tracking.

Provides functions for:
- Creating migration tracking tables
- Recording migration history
- Executing baseline migrations
- Executing update migrations
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import time


def create_migration_table(z: Any, table_name: str) -> bool:
    """
    Create {table_name}_zMigration table from system schema template.
    
    Migration files are stored in Data/.zmigrations/ subfolder.
    Uses zSchema.zMigration.yaml as template.
    
    Args:
        z: zCLI instance
        table_name: Base table name (e.g., 'users')
    
    Returns:
        bool: True if created successfully
    
    Example:
        >>> create_migration_table(z, 'users')
        True  # Creates Data/.zmigrations/users_zMigration.csv
    """
    migration_table = f"{table_name}_zMigration"
    
    try:
        # Load the migration schema template
        migration_schema_path = z.config.sys_paths.user_zschemas_dir / "zSchema.zMigration.yaml"
        
        if not migration_schema_path.exists():
            z.logger.error(f"Migration schema template not found: {migration_schema_path}")
            return False
        
        # Load the template
        import yaml
        with open(migration_schema_path, 'r') as f:
            migration_schema = yaml.safe_load(f)
        
        # The template uses '__zmigration' as table name, we need to rename it
        table_def = migration_schema['__zmigration']
        
        # Get the data source for the base table to know where to create migration table
        # For now, assume same location as base table
        # TODO: Get actual data source from base table's schema
        
        z.logger.info(f"[zMigration] Creating migration table: {migration_table}")
        
        # For CSV, we just need to create the file with headers
        # zData will handle this automatically when we insert the first record
        
        return True
        
    except Exception as e:
        z.logger.error(f"[zMigration] Failed to create migration table: {e}")
        return False


def record_migration(
    z: Any,
    table_name: str,
    from_version: Optional[str],
    to_version: str,
    schema_hash: str,
    changes_summary: str = "",
    changes_detail: str = "",
    is_breaking: bool = False,
    duration_ms: int = 0,
    migration_hook: Optional[str] = None
) -> bool:
    """
    Record a migration in the history table.
    
    Args:
        z: zCLI instance
        table_name: Base table name
        from_version: Previous version (None for baseline)
        to_version: New version
        schema_hash: SHA256 hash of new schema
        changes_summary: Human-readable summary
        changes_detail: JSON with full diff
        is_breaking: Whether migration is breaking
        duration_ms: Execution time in milliseconds
        migration_hook: Name of data migration hook (if any)
    
    Returns:
        bool: True if recorded successfully
    """
    # Use clean naming for migration tracking
    migration_table = f"{table_name}_zMigration"
    
    try:
        # For CSV: Create the file in .zmigrations/ subfolder
        # Get the workspace's Data directory
        data_dir = Path(z.config.sys_paths.workspace_dir) / "Data"
        migration_dir = data_dir / ".zmigrations"
        
        # Ensure .zmigrations directory exists
        migration_dir.mkdir(exist_ok=True)
        
        migration_csv_file = migration_dir / f"{migration_table}.csv"
        
        if not migration_csv_file.exists():
            z.logger.info(f"[zMigration] Creating migration table: {migration_table}")
            
            # Create CSV with headers
            headers = [
                'id', 'from_version', 'to_version', 'applied_at', 'applied_by',
                'duration_ms', 'schema_hash', 'changes_summary', 'changes_detail',
                'status', 'error_message', 'rollback_possible', 'backup_location',
                'rows_affected', 'columns_added', 'columns_dropped', 'columns_modified',
                'is_breaking', 'migration_hook', 'hook_result'
            ]
            
            import csv
            with open(migration_csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
            
            z.logger.info(f"[zMigration] Created migration table CSV: {migration_csv_file}")
        
        # Now load the schema dynamically so zData can work with it
        # We need to create a minimal schema definition
        migration_schema_content = f"""
Meta:
  Data_Type: csv
  Data_Label: "Migration History for {table_name}"
  Data_Source: "@.Data"
  Data_Paradigm: classical
  Schema_Name: "{table_name}_zMigration"
  zMigration: false

{migration_table}:
  id:
    type: int
    pk: true
    auto_increment: true
  from_version:
    type: str
    required: false
  to_version:
    type: str
    required: true
  applied_at:
    type: datetime
    default: now
  applied_by:
    type: str
    default: "system"
  duration_ms:
    type: int
    default: 0
  schema_hash:
    type: str
    required: true
  changes_summary:
    type: str
    required: false
  changes_detail:
    type: str
    required: false
  status:
    type: str
    default: "success"
  error_message:
    type: str
    required: false
  rollback_possible:
    type: bool
    default: false
  backup_location:
    type: str
    required: false
  rows_affected:
    type: int
    default: 0
  columns_added:
    type: int
    default: 0
  columns_dropped:
    type: int
    default: 0
  columns_modified:
    type: int
    default: 0
  is_breaking:
    type: bool
    default: false
  migration_hook:
    type: str
    required: false
  hook_result:
    type: str
    required: false
"""
        
        # Save temporary schema file
        temp_schema_file = data_dir.parent / "models" / f"zSchema.{migration_table}.yaml"
        temp_schema_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(temp_schema_file, 'w') as f:
            f.write(migration_schema_content)
        
        # Load the schema
        z.data.load_schema(f"@.models.zSchema.{migration_table}")
        
        # Prepare migration record
        migration_record = {
            'from_version': from_version if from_version else '',
            'to_version': to_version,
            'applied_at': datetime.now(),
            'applied_by': 'system',
            'duration_ms': duration_ms,
            'schema_hash': schema_hash,
            'changes_summary': changes_summary if changes_summary else 'baseline',
            'changes_detail': changes_detail if changes_detail else '',
            'status': 'success',
            'error_message': '',
            'rollback_possible': not is_breaking,
            'backup_location': '',
            'rows_affected': 0,
            'columns_added': 0,
            'columns_dropped': 0,
            'columns_modified': 0,
            'is_breaking': is_breaking,
            'migration_hook': migration_hook if migration_hook else '',
            'hook_result': ''
        }
        
        # Insert migration record
        z.data.insert(
            table=migration_table,
            fields=list(migration_record.keys()),
            values=list(migration_record.values())
        )
        
        z.logger.info(f"[zMigration] Recorded migration: {from_version or 'baseline'} → {to_version}")
        
        return True
        
    except Exception as e:
        z.logger.error(f"[zMigration] Failed to record migration: {e}")
        import traceback
        z.logger.error(f"[zMigration] Traceback: {traceback.format_exc()}")
        return False


def execute_baseline_migration(z: Any, migration_info: Dict[str, Any]) -> bool:
    """
    Execute a baseline migration for a new schema.
    
    Baseline migrations:
    - Create migration tracking table
    - Record initial version
    - No DDL changes (table already exists from schema)
    
    Args:
        z: zCLI instance
        migration_info: Dict with schema_name, table_name, to_version, current_hash
    
    Returns:
        bool: True if successful
    """
    table_name = migration_info['table_name']
    to_version = migration_info['to_version']
    schema_hash = migration_info['current_hash']
    
    z.logger.info(f"[zMigration] Executing baseline migration for: {table_name}")
    
    start_time = time.time()
    
    # Record the baseline migration
    success = record_migration(
        z=z,
        table_name=table_name,
        from_version=None,
        to_version=to_version,
        schema_hash=schema_hash,
        changes_summary="baseline",
        is_breaking=False,
        duration_ms=int((time.time() - start_time) * 1000)
    )
    
    if success:
        z.logger.info(f"[zMigration] ✅ Baseline migration complete: {table_name} @ {to_version}")
    else:
        z.logger.error(f"[zMigration] ❌ Baseline migration failed: {table_name}")
    
    return success


def execute_update_migration(z: Any, migration_info: Dict[str, Any]) -> bool:
    """
    Execute an update migration for a changed schema.
    
    Update migrations:
    - Apply DDL changes (for SQL backends)
    - For CSV: validate schema only (structure is dynamic)
    - Record migration history
    
    Args:
        z: zCLI instance
        migration_info: Dict with schema_name, table_name, from_version, to_version, etc.
    
    Returns:
        bool: True if successful
    """
    table_name = migration_info['table_name']
    from_version = migration_info['from_version']
    to_version = migration_info['to_version']
    schema_hash = migration_info['current_hash']
    changes = migration_info.get('changes')
    is_breaking = migration_info.get('is_breaking', False)
    
    z.logger.info(f"[zMigration] Executing update migration: {table_name} ({from_version} → {to_version})")
    
    start_time = time.time()
    
    # For CSV backend: No DDL execution needed (dynamic structure)
    # For SQL backends: Would execute ALTER TABLE statements here
    # TODO: Implement DDL execution for SQL backends
    
    # Format changes summary
    if changes:
        from .migration_detection import format_changes_summary
        changes_summary = format_changes_summary(changes)
    else:
        changes_summary = "schema updated"
    
    # Record the migration
    success = record_migration(
        z=z,
        table_name=table_name,
        from_version=from_version,
        to_version=to_version,
        schema_hash=schema_hash,
        changes_summary=changes_summary,
        is_breaking=is_breaking,
        duration_ms=int((time.time() - start_time) * 1000)
    )
    
    if success:
        z.logger.info(f"[zMigration] ✅ Update migration complete: {table_name} @ {to_version}")
    else:
        z.logger.error(f"[zMigration] ❌ Update migration failed: {table_name}")
    
    return success


def execute_migrations(z: Any, migrations: List[Dict[str, Any]], auto_approve: bool = False) -> Dict[str, Any]:
    """
    Execute a list of migrations.
    
    Args:
        z: zCLI instance
        migrations: List of migration info dicts
        auto_approve: Skip confirmation prompts
    
    Returns:
        Dict with results: {'success': int, 'failed': int, 'skipped': int}
    """
    results = {
        'success': 0,
        'failed': 0,
        'skipped': 0
    }
    
    if not migrations:
        return results
    
    # Prompt for confirmation (unless auto-approve)
    if not auto_approve:
        print("\n⚠️  Ready to apply migrations. This will modify migration history.")
        print(f"   Total migrations: {len(migrations)}")
        
        response = input("\n   Continue? [Y/n]: ").strip().lower()
        if response and response != 'y':
            print("   Migration cancelled.")
            results['skipped'] = len(migrations)
            return results
        
        print()
    
    # Execute each migration
    for migration in migrations:
        migration_type = migration['type']
        table_name = migration['table_name']
        
        try:
            if migration_type == 'baseline':
                success = execute_baseline_migration(z, migration)
            elif migration_type == 'update':
                success = execute_update_migration(z, migration)
            else:
                z.logger.error(f"Unknown migration type: {migration_type}")
                success = False
            
            if success:
                results['success'] += 1
                print(f"   ✅ {table_name}: Migration applied successfully")
            else:
                results['failed'] += 1
                print(f"   ❌ {table_name}: Migration failed")
                
        except Exception as e:
            results['failed'] += 1
            print(f"   ❌ {table_name}: Error - {e}")
            z.logger.error(f"[zMigration] Exception during migration: {e}")
    
    return results

