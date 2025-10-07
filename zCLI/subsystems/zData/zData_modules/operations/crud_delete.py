# zCLI/crud/crud_delete.py — Delete, Truncate, and List Operations
# ───────────────────────────────────────────────────────────────

from logger import Logger
from zCLI.subsystems.zDisplay import handle_zDisplay
from .crud_where import build_where_clause


def zDelete(zRequest, zForm, zData):
    handle_zDisplay({
        "event": "sysmsg",
        "style": "single",
        "label": "zDelete",
        "color": "ZCRUD",
        "indent": 4
    })

    if not zData or not zData.get("ready"):
        logger.error("No valid DB connection found.")
        return 0

    data_type = zData.get("type")
    if data_type == "sqlite":
        return zDelete_sqlite(zRequest, zForm, zData)

    logger.warning("zDelete not implemented for data type: %s", data_type)
    return 0


def zDelete_sqlite(zRequest, zForm, zData):
    cur = zData["cursor"]
    conn = zData["conn"]

    tables = zRequest.get("tables")
    if not tables:
        model = zRequest.get("model")
        inferred = model.split(".")[-1] if isinstance(model, str) else None
        if not inferred:
            logger.error("No table specified and unable to infer from model.")
            return 0
        tables = [inferred]

    table = tables[0]

    # Build WHERE clause with advanced operators support
    filters = zRequest.get("where") or zRequest.get("filters")
    where_clause, params = build_where_clause(filters)

    sql = f"DELETE FROM {table}{where_clause};"
    logger.info("Executing SQL: %s | params: %s", sql, params)

    try:
        cur.execute(sql, params)
        conn.commit()
        logger.info("Rows deleted: %d", cur.rowcount)
        return cur.rowcount
    except Exception as e:
        logger.error("Delete failed for table '%s' with error: %s", table, e)
        return 0


def zTruncate(zRequest, zForm, zData):
    handle_zDisplay({
        "event": "sysmsg",
        "style": "single",
        "label": "zTruncate",
        "color": "ZCRUD",
        "indent": 4,
    })

    if not zData or not zData.get("ready"):
        logger.error("No valid DB connection found.")
        return 0

    data_type = zData.get("type")
    if data_type == "sqlite":
        return zTruncate_sqlite(zRequest, zForm, zData)

    logger.warning("zTruncate not implemented for data type: %s", data_type)
    return 0


def zTruncate_sqlite(zRequest, zForm, zData):
    cur = zData["cursor"]
    conn = zData["conn"]

    tables = zRequest.get("tables")
    if not tables:
        model = zRequest.get("model")
        inferred = model.split(".")[-1] if isinstance(model, str) else None
        if not inferred:
            logger.error("No table specified and unable to infer from model.")
            return 0
        tables = [inferred]

    table = tables[0]

    sql = f"DELETE FROM {table};"
    logger.info("Executing SQL: %s", sql)

    try:
        cur.execute(sql)
        conn.commit()
        logger.info("Table truncated: %s | rows deleted: %d", table, cur.rowcount)
        return cur.rowcount
    except Exception as e:
        logger.error("Truncate failed for table '%s' with error: %s", table, e)
        return 0


def zListTables(zForm, zData):
    handle_zDisplay({
        "event": "sysmsg",
        "style": "single",
        "label": "zListTables",
        "color": "ZCRUD",
        "indent": 3,
    })

    if not zData or not zData.get("ready"):
        logger.error("No valid DB connection found.")
        return []

    data_type = zData.get("type")
    if data_type == "sqlite":
        cur = zData["cursor"]
        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        logger.info("Executing SQL: %s", sql)
        try:
            cur.execute(sql)
            rows = [r[0] for r in cur.fetchall()]
            handle_zDisplay({
                "event": "zJSON",
                "title": "Tables",
                "payload": rows,
                "color": "CYAN",
                "style": "~",
                "indent": 0,
            })
            logger.info("Tables listed: %d", len(rows))
            return rows
        except Exception as e:
            logger.error("Failed to list tables with error: %s", e)
            return []

    logger.warning("zListTables not implemented for data type: %s", data_type)
    return []

