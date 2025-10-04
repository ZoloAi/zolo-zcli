# zCLI/crud/crud_read.py — Read and Search Operations
# ───────────────────────────────────────────────────────────────

from zCLI.utils.logger import logger
from zCLI.subsystems.zDisplay import handle_zDisplay
from zCLI.subsystems.zSession import zSession
from .crud_handler import build_order_clause
from .crud_join import build_join_clause, build_select_with_tables
from .crud_where import build_where_clause


def zRead(zRequest, zForm, zData, walker=None):
    handle_zDisplay({
        "event": "header",
        "style": "single",
        "label": "zRead",
        "color": "ZCRUD",
        "indent": 4
    })

    logger.info("zRead start; zRequest=%s", zRequest)

    if not zData or not zData.get("ready"):
        logger.error("No valid DB connection found.")
        return []

    cur = zData["cursor"]
    logger.info("DB type: %s | DB path: %s", zData.get("type"), zData.get("path"))

    # ── 1) Resolve target table (explicit or inferred from model)
    tables = zRequest.get("tables")
    if not tables:
        model = zRequest.get("model")
        inferred = model.split(".")[-1] if isinstance(model, str) else None
        logger.info("No 'tables' provided; model=%s → inferred_table=%s", model, inferred)
        if not inferred:
            logger.error("No table specified and unable to infer from model.")
            return []
        tables = [inferred]
    else:
        logger.info("'tables' provided: %s", tables)
    
    # ── 1.5) Check for JOIN support (Phase 2)
    joins = zRequest.get("joins")
    auto_join = zRequest.get("auto_join", False)
    
    if len(tables) > 1 or joins or auto_join:
        # Multi-table query with JOINs
        logger.info("🔗 Multi-table query detected - using JOIN logic")
        return zReadJoin(zRequest, zForm, zData, walker=walker)

    table = tables[0]
    logger.info("Target table: %s", table)

    # ── 2) Fields (defaults to '*'); normalize dotted names ('tbl.col' -> 'col')
    raw_fields = zRequest.get("fields") or ["*"]
    logger.info("Raw fields from request: %s", raw_fields)

    fields = [f.split(".")[-1] for f in raw_fields if isinstance(f, str)]
    select_clause = "*" if fields == ["*"] or not fields else ", ".join(fields)
    logger.info("Select clause: %s", select_clause)

    # ── 3) WHERE filters (Advanced operators support)
    filters = zRequest.get("where") or zRequest.get("filters")
    where_clause, params = build_where_clause(filters)
    logger.info("WHERE clause: %s | params: %s", where_clause or "<none>", params)
    
    # ── 4) ORDER BY
    order_clause = build_order_clause(zRequest.get("order_by"))
    logger.info("ORDER BY clause: %s", order_clause or "<none>")

    # ── 5) Pagination (LIMIT/OFFSET)
    limit = zRequest.get("limit")
    offset = zRequest.get("offset")
    per_page = zRequest.get("perPage")  # New: perPage support
    
    # Convert perPage to limit if provided
    if per_page and not limit:
        limit = int(per_page)
    
    logger.info("Pagination request: limit=%s, offset=%s, perPage=%s", limit, offset, per_page)

    limit_sql = ""
    if isinstance(limit, int) and limit > 0:
        limit_sql = " LIMIT ?"
        params.append(limit)
        if isinstance(offset, int) and offset >= 0:
            limit_sql += " OFFSET ?"
            params.append(offset)

    # ── 6) Build + execute
    sql = f"SELECT {select_clause} FROM {table}{where_clause}{order_clause}{limit_sql};"
    logger.info("Executing SQL: %s | params: %s", sql, params)

    try:
        cur.execute(sql, params)
        rows = cur.fetchall()
        colnames = [d[0] for d in cur.description] if cur.description else []
        logger.info("Query succeeded. Columns=%s", colnames)
        logger.info("Rows fetched: %d", len(rows))

        result = [dict(zip(colnames, r)) for r in rows] if colnames else []

        # ── 7) Render result to UI with pagination info
        pagination_info = ""
        if limit:
            current_page = (offset // limit) + 1 if offset else 1
            pagination_info = f" (Page {current_page}, {len(result)} of {limit} per page)"
        
        # Check if we're in a terminal session and display as table instead of JSON
        # Use walker's session if available, otherwise fall back to global
        target_session = walker.zSession if (walker and hasattr(walker, 'zSession')) else zSession
        session_type = target_session.get("zMode", "unknown")
        
        if session_type == "Terminal" and result:
            handle_zDisplay({
                "event": "zTable",
                "title": f"{table} rows{pagination_info}",
                "payload": result,
                "color": "CYAN",
                "style": "~",
                "indent": 0
            })
        else:
            handle_zDisplay({
                "event": "zJSON",
                "title": f"{table} rows{pagination_info}",
                "payload": result,
                "color": "CYAN",
                "style": "~",
                "indent": 0
            })
        
        # ── 8) Add pause for user to read results with navigation if needed
        # Only pause if explicitly requested via pause=True parameter (defaults to False)
        should_pause = zRequest.get("pause", False)
        logger.info("Pause parameter: %s", should_pause)
        
        if result and should_pause:
            # Check if there might be more pages (if we got exactly the limit, there might be more)
            has_more_pages = limit and len(result) == limit
            current_page = (offset // limit) + 1 if offset and limit else 1
            
            pause_result = handle_zDisplay({
                "event": "pause",
                "message": f"📊 Showing {len(result)} results",
                "color": "INFO",
                "indent": 1,
                "pagination": {
                    "has_more_pages": has_more_pages,
                    "current_page": current_page,
                    "limit": limit,
                    "offset": offset,
                    "result_count": len(result),
                    "table": table,
                    "zRequest": zRequest  # Pass the original request for navigation
                }
            })
            
            # Handle navigation if user chose to navigate
            if isinstance(pause_result, dict) and pause_result.get("action") == "navigate":
                # Update the request with new offset and recursively call zRead
                nav_zRequest = dict(zRequest)  # Copy the original request
                nav_zRequest["offset"] = pause_result.get("offset", 0)
                logger.info("Navigating to page with offset: %s", nav_zRequest["offset"])
                return zRead(nav_zRequest, zForm, zData)  # Recursive call with new offset
            elif pause_result == "exit":
                logger.info("User chose to exit pagination")
                return result
        
        logger.info("zRead finished for table: %s", table)
        return result

    except Exception as e:
        logger.error("Read failed for table '%s' with error: %s", table, e)
        return []


def zReadJoin(zRequest, zForm, zData, walker=None):
    """
    Read operation with JOIN support for multi-table queries.
    
    Args:
        zRequest: Request with tables, joins, fields, where, etc.
        zForm: Parsed schema
        zData: Database connection
        walker: Optional walker for session context
        
    Returns:
        list: Query results
    """
    handle_zDisplay({
        "event": "header",
        "style": "single",
        "label": "zRead (JOIN)",
        "color": "ZCRUD",
        "indent": 4
    })
    
    logger.info("🔗 zReadJoin start; zRequest=%s", zRequest)
    
    if not zData or not zData.get("ready"):
        logger.error("No valid DB connection found.")
        return []
    
    cur = zData["cursor"]
    
    # ── 1) Get tables
    tables = zRequest.get("tables", [])
    if len(tables) < 2 and not zRequest.get("joins"):
        logger.warning("JOIN query requires multiple tables")
        return []
    
    # ── 2) Build JOIN clause
    joins = zRequest.get("joins")
    auto_join = zRequest.get("auto_join", False)
    
    from_clause, joined_tables = build_join_clause(
        tables=tables,
        joins=joins,
        schema=zForm,
        auto_join=auto_join
    )
    
    logger.info("FROM clause with JOINs: %s", from_clause)
    
    # ── 3) Build SELECT clause with table qualifiers
    raw_fields = zRequest.get("fields") or ["*"]
    select_clause = build_select_with_tables(raw_fields, tables)
    logger.info("SELECT clause: %s", select_clause)
    
    # ── 4) Build WHERE clause (supports table-qualified fields and advanced operators)
    filters = zRequest.get("where") or zRequest.get("filters")
    where_clause, params = build_where_clause(filters)
    logger.info("WHERE clause: %s | params: %s", where_clause or "<none>", params)
    
    # ── 5) ORDER BY
    order_clause = build_order_clause(zRequest.get("order_by"))
    logger.info("ORDER BY clause: %s", order_clause or "<none>")
    
    # ── 6) Pagination
    limit = zRequest.get("limit")
    offset = zRequest.get("offset")
    per_page = zRequest.get("perPage")
    
    if per_page and not limit:
        limit = int(per_page)
    
    logger.info("Pagination: limit=%s, offset=%s", limit, offset)
    
    limit_sql = ""
    if isinstance(limit, int) and limit > 0:
        limit_sql = " LIMIT ?"
        params.append(limit)
        if isinstance(offset, int) and offset >= 0:
            limit_sql += " OFFSET ?"
            params.append(offset)
    
    # ── 7) Build and execute query
    sql = f"SELECT {select_clause} FROM {from_clause}{where_clause}{order_clause}{limit_sql};"
    logger.info("Executing JOIN SQL: %s | params: %s", sql, params)
    
    try:
        cur.execute(sql, params)
        rows = cur.fetchall()
        colnames = [d[0] for d in cur.description] if cur.description else []
        logger.info("JOIN query succeeded. Columns=%s", colnames)
        logger.info("Rows fetched: %d", len(rows))
        
        result = [dict(zip(colnames, r)) for r in rows] if colnames else []
        
        # ── 8) Display results
        pagination_info = ""
        if limit:
            current_page = (offset // limit) + 1 if offset else 1
            pagination_info = f" (Page {current_page}, {len(result)} of {limit} per page)"
        
        # Check session mode for display
        target_session = walker.zSession if (walker and hasattr(walker, 'zSession')) else zSession
        session_type = target_session.get("zMode", "unknown")
        
        table_name = " + ".join(tables)  # Show joined tables
        
        if session_type == "Terminal" and result:
            handle_zDisplay({
                "event": "zTable",
                "title": f"{table_name} (joined){pagination_info}",
                "payload": result,
                "color": "CYAN",
                "style": "~",
                "indent": 0
            })
        else:
            handle_zDisplay({
                "event": "zJSON",
                "title": f"{table_name} (joined){pagination_info}",
                "payload": result,
                "color": "CYAN",
                "style": "~",
                "indent": 0
            })
        
        # ── 9) Optional pause
        should_pause = zRequest.get("pause", False)
        if result and should_pause and session_type == "Terminal":
            from zCLI.subsystems.zDisplay import handle_zInput
            handle_zInput({
                "event": "break"
            })
        
        logger.info("zReadJoin finished for tables: %s", tables)
        return result
    
    except Exception as e:
        logger.error("JOIN query failed: %s", e)
        logger.error("SQL was: %s", sql)
        return []


def zSearch(zRequest, zForm, zData):
    handle_zDisplay({
        "event": "header",
        "style": "single",
        "label": "zSearch",
        "color": "ZCRUD",
        "indent": 4,
    })

    if not zData or not zData.get("ready"):
        logger.error("No valid DB connection found.")
        return []

    data_type = zData.get("type")
    if data_type == "sqlite":
        return zSearch_sqlite(zRequest, zForm, zData)

    logger.warning("zSearch not implemented for data type: %s", data_type)
    return []


def zSearch_sqlite(zRequest, zForm, zData):
    cur = zData["cursor"]

    tables = zRequest.get("tables")
    if not tables:
        model = zRequest.get("model")
        inferred = model.split(".")[-1] if isinstance(model, str) else None
        if not inferred:
            logger.error("No table specified and unable to infer from model.")
            return []
        tables = [inferred]

    table = tables[0]

    raw_fields = zRequest.get("fields") or ["*"]
    fields = [f.split(".")[-1] for f in raw_fields if isinstance(f, str)]
    select_clause = "*" if fields == ["*"] or not fields else ", ".join(fields)

    search = zRequest.get("search") or {}
    where_clause = ""
    params = []
    if isinstance(search, dict) and search:
        conds = []
        for key, val in search.items():
            col = key.split(".")[-1]
            conds.append(f"{col} LIKE ?")
            params.append(f"%{val}%")
        where_clause = " WHERE " + " AND ".join(conds)
    
    order_clause = build_order_clause(zRequest.get("order_by"))
    logger.info("ORDER BY clause: %s", order_clause or "<none>")

    limit = zRequest.get("limit")
    offset = zRequest.get("offset")
    per_page = zRequest.get("perPage")  # New: perPage support
    
    # Convert perPage to limit if provided
    if per_page and not limit:
        limit = int(per_page)
    
    limit_sql = ""
    if isinstance(limit, int) and limit > 0:
        limit_sql = " LIMIT ?"
        params.append(limit)
        if isinstance(offset, int) and offset >= 0:
            limit_sql += " OFFSET ?"
            params.append(offset)

    sql = f"SELECT {select_clause} FROM {table}{where_clause}{order_clause}{limit_sql};"
    logger.info("Executing SQL: %s | params: %s", sql, params)

    try:
        cur.execute(sql, params)
        rows = cur.fetchall()
        colnames = [d[0] for d in cur.description] if cur.description else []
        result = [dict(zip(colnames, r)) for r in rows] if colnames else []

        handle_zDisplay({
            "event": "zJSON",
            "title": f"{table} rows",
            "payload": result,
            "color": "CYAN",
            "style": "~",
            "indent": 0,
        })
        logger.info("zSearch finished for table: %s", table)
        return result
    except Exception as e:
        logger.error("Search failed for table '%s' with error: %s", table, e)
        return []

