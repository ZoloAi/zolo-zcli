# zCLI/crud/crud_update.py — Update Operations
# ───────────────────────────────────────────────────────────────

from zCLI.utils.logger import logger
from zCLI.subsystems.zDisplay import handle_zDisplay


def zUpdate(zRequest, zForm, zData):
    handle_zDisplay({
        "event": "header",
        "style": "single",
        "label": "zUpdate",
        "color": "ZCRUD",
        "indent": 4
    })

    if not zData or not zData.get("ready"):
        logger.error("No valid DB connection found.")
        return 0

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

    values = zRequest.get("values")
    if not isinstance(values, dict) or not values:
        logger.error("No values provided for update.")
        return 0

    set_parts = []
    params = []
    for key, val in values.items():
        col = key.split(".")[-1]
        set_parts.append(f"{col} = ?")
        params.append(val)

    set_clause = ", ".join(set_parts)

    filters = zRequest.get("where") or zRequest.get("filters")
    where_clause = ""
    if isinstance(filters, dict) and filters:
        conds = []
        for key, val in filters.items():
            col = key.split(".")[-1]
            conds.append(f"{col} = ?")
            params.append(val)
        where_clause = " WHERE " + " AND ".join(conds)

    sql = f"UPDATE {table} SET {set_clause}{where_clause};"
    logger.info("Executing SQL: %s | params: %s", sql, params)

    try:
        cur.execute(sql, params)
        conn.commit()
        logger.info("Rows updated: %d", cur.rowcount)
        return cur.rowcount
    except Exception as e:
        logger.error("Update failed for table '%s' with error: %s", table, e)
        return 0

