# zCLI/subsystems/zSchema_modules/fk_resolver.py — Foreign Key Resolution
# ----------------------------------------------------------------
# Handles resolution of foreign key fields and their referenced data.
# 
# Functions:
# - resolve_fk_fields(): Resolve FK fields and load referenced table data
# ----------------------------------------------------------------

import sqlite3
from zCLI.utils.logger import logger
from zCLI.subsystems.zParser import handle_zRef
from zCLI.subsystems.zDisplay import Colors, print_line


def resolve_fk_fields(schema: dict, db_path: str) -> dict:
    """
    Resolves all fields in a schema that have a 'fk' key by:
    - Loading the referenced foreign table's schema via 'source'
    - Selecting (id, label) tuples from that table to offer as options

    Returns:
        dict: {
            field_name: {
                "options": [(id, label), ...],
                "schema": foreign_schema
            }, ...
        }
    """
    print_line(Colors.SCHEMA, "resolve_fk_fields", "single", indent=6)

    fk_fields = {k: v for k, v in schema.items() if "fk" in v and "source" in v}
    resolved = {}

    for field, meta in fk_fields.items():
        fk_target = meta["fk"]        # e.g., "zUsers.id"
        schema_path = meta["source"]  # e.g., "zCloud.schemas.schema.zIndex.zUsers"

        logger.info(f"🔗 Resolving FK for '{field}' → {fk_target} via {schema_path}")

        foreign_schema_ref = handle_zRef(schema_path)
        if not foreign_schema_ref:
            logger.warning(f"⚠️ Could not resolve FK schema from: {schema_path}")
            continue

        foreign_schema = foreign_schema_ref.get("schema", {})
        foreign_db_path = foreign_schema_ref.get("db_path", db_path)
        foreign_table = fk_target.split(".")[0].split("/")[-1]
        id_field = fk_target.split(".")[-1]

        # Try to pick a friendly label field
        label_field = next(
            (f for f in ("name", "username", "title", "label") if f in foreign_schema),
            id_field
        )

        sql = f"SELECT {id_field}, {label_field} FROM {foreign_table}"

        try:
            conn = sqlite3.connect(foreign_db_path)
            cur = conn.cursor()
            cur.execute(sql)
            options = cur.fetchall()
            conn.close()

            resolved[field] = {
                "options": [(id_, label) for id_, label in options],
                "schema": foreign_schema_ref
            }

            logger.info(f"✅ Resolved {len(options)} FK options for '{field}'")

        except (sqlite3.Error, OSError, ValueError) as e:
            logger.error(f"❌ FK resolution failed for '{field}': {e}")

    return resolved
