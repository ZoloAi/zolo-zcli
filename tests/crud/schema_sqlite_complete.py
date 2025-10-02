#!/usr/bin/env python3
"""
Complete SQLite Schema Reference - Industry Standard
=====================================================

This file demonstrates ALL SQLite features and capabilities for schema definition.
Use this as a reference for building migration and schema management systems.

SQLite Version: 3.35+ (with modern features)
Format: Python schema definition (SQLAlchemy-style but pure SQLite)

Features Covered:
- All data types (INTEGER, TEXT, REAL, BLOB, NUMERIC)
- Primary keys (simple, composite, AUTOINCREMENT)
- Foreign keys (all ON DELETE/UPDATE actions)
- Constraints (UNIQUE, NOT NULL, CHECK, DEFAULT)
- Indexes (simple, composite, unique, partial, expression)
- Generated columns (VIRTUAL, STORED)
- Triggers (BEFORE, AFTER, INSTEAD OF)
- Views (simple, complex with JOINs)
- STRICT tables (type enforcement)
- WITHOUT ROWID optimization
- Collation sequences
- Partial indexes with WHERE
- Full-text search (FTS5)
"""

import sqlite3
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════
# SCHEMA DEFINITION
# ═══════════════════════════════════════════════════════════════════

SCHEMA = {
    # ─────────────────────────────────────────────────────────────
    # TABLE 1: Users - Comprehensive Column Types and Constraints
    # ─────────────────────────────────────────────────────────────
    "users": {
        "table_name": "users",
        "columns": [
            # INTEGER Types
            {
                "name": "id",
                "type": "INTEGER",
                "primary_key": True,
                "autoincrement": True,  # SQLite AUTOINCREMENT
                "not_null": True
            },
            {
                "name": "age",
                "type": "INTEGER",
                "check": "age >= 18 AND age <= 120",  # CHECK constraint
                "default": None
            },
            {
                "name": "login_count",
                "type": "INTEGER",
                "not_null": True,
                "default": 0
            },
            
            # TEXT Types
            {
                "name": "username",
                "type": "TEXT",
                "not_null": True,
                "unique": True,  # UNIQUE constraint
                "collate": "NOCASE"  # Case-insensitive collation
            },
            {
                "name": "email",
                "type": "TEXT",
                "not_null": True,
                "unique": True,
                "check": "email LIKE '%@%'"  # Simple email validation
            },
            {
                "name": "password_hash",
                "type": "TEXT",
                "not_null": True
            },
            {
                "name": "bio",
                "type": "TEXT",
                "default": "'No bio provided'",  # TEXT default
                "check": "LENGTH(bio) <= 500"
            },
            
            # REAL (Float) Type
            {
                "name": "rating",
                "type": "REAL",
                "check": "rating >= 0.0 AND rating <= 5.0",
                "default": 0.0
            },
            
            # BLOB Type
            {
                "name": "avatar",
                "type": "BLOB",  # Binary data (images, files)
                "default": None
            },
            
            # NUMERIC Type (flexible numeric)
            {
                "name": "balance",
                "type": "NUMERIC",
                "not_null": True,
                "default": 0.00,
                "check": "balance >= 0"
            },
            
            # Timestamps
            {
                "name": "created_at",
                "type": "TEXT",  # ISO8601 strings for SQLite
                "not_null": True,
                "default": "CURRENT_TIMESTAMP"  # SQLite function
            },
            {
                "name": "updated_at",
                "type": "TEXT",
                "default": "CURRENT_TIMESTAMP"
            },
            {
                "name": "last_login",
                "type": "TEXT",
                "default": None
            },
            
            # Boolean (stored as INTEGER 0/1 in SQLite)
            {
                "name": "is_active",
                "type": "INTEGER",
                "not_null": True,
                "default": 1,
                "check": "is_active IN (0, 1)"  # Enforce boolean values
            },
            {
                "name": "is_verified",
                "type": "INTEGER",
                "default": 0,
                "check": "is_verified IN (0, 1)"
            },
            
            # ENUM-like (using CHECK constraint)
            {
                "name": "role",
                "type": "TEXT",
                "not_null": True,
                "default": "'user'",
                "check": "role IN ('admin', 'moderator', 'user', 'guest')"
            },
            {
                "name": "status",
                "type": "TEXT",
                "default": "'active'",
                "check": "status IN ('active', 'suspended', 'deleted')"
            }
        ],
        "indexes": [
            # Simple index
            {"name": "idx_users_username", "columns": ["username"]},
            # Composite index
            {"name": "idx_users_email_status", "columns": ["email", "status"]},
            # Unique index (alternative to column-level UNIQUE)
            {"name": "idx_users_email_unique", "columns": ["email"], "unique": True},
            # Partial index (SQLite 3.8+)
            {"name": "idx_users_active", "columns": ["status"], "where": "status = 'active'"},
            # Expression index (SQLite 3.9+)
            {"name": "idx_users_lower_username", "expression": "LOWER(username)"}
        ],
        "options": {
            "strict": False,  # STRICT tables (SQLite 3.37+) - enforce type checking
            "without_rowid": False  # WITHOUT ROWID optimization
        }
    },
    
    # ─────────────────────────────────────────────────────────────
    # TABLE 2: Posts - Foreign Keys and ON DELETE/UPDATE Actions
    # ─────────────────────────────────────────────────────────────
    "posts": {
        "table_name": "posts",
        "columns": [
            {
                "name": "id",
                "type": "INTEGER",
                "primary_key": True,
                "autoincrement": True
            },
            {
                "name": "user_id",
                "type": "INTEGER",
                "not_null": True,
                "foreign_key": {
                    "table": "users",
                    "column": "id",
                    "on_delete": "CASCADE",  # Delete posts when user deleted
                    "on_update": "CASCADE"   # Update post.user_id if users.id changes
                }
            },
            {
                "name": "title",
                "type": "TEXT",
                "not_null": True,
                "check": "LENGTH(title) >= 3 AND LENGTH(title) <= 200"
            },
            {
                "name": "content",
                "type": "TEXT",
                "not_null": True
            },
            {
                "name": "view_count",
                "type": "INTEGER",
                "not_null": True,
                "default": 0
            },
            {
                "name": "published_at",
                "type": "TEXT",
                "default": None
            },
            {
                "name": "created_at",
                "type": "TEXT",
                "not_null": True,
                "default": "CURRENT_TIMESTAMP"
            }
        ],
        "indexes": [
            {"name": "idx_posts_user_id", "columns": ["user_id"]},
            {"name": "idx_posts_published", "columns": ["published_at"], "where": "published_at IS NOT NULL"}
        ]
    },
    
    # ─────────────────────────────────────────────────────────────
    # TABLE 3: Comments - Composite Primary Key & Self-Reference
    # ─────────────────────────────────────────────────────────────
    "comments": {
        "table_name": "comments",
        "columns": [
            {
                "name": "id",
                "type": "INTEGER",
                "not_null": True
            },
            {
                "name": "post_id",
                "type": "INTEGER",
                "not_null": True,
                "foreign_key": {
                    "table": "posts",
                    "column": "id",
                    "on_delete": "CASCADE"  # Delete comments when post deleted
                }
            },
            {
                "name": "user_id",
                "type": "INTEGER",
                "not_null": True,
                "foreign_key": {
                    "table": "users",
                    "column": "id",
                    "on_delete": "SET NULL"  # Keep comment but nullify user
                }
            },
            {
                "name": "parent_comment_id",
                "type": "INTEGER",
                "default": None,
                "foreign_key": {
                    "table": "comments",  # Self-reference for nested comments
                    "column": "id",
                    "on_delete": "CASCADE"
                }
            },
            {
                "name": "content",
                "type": "TEXT",
                "not_null": True,
                "check": "LENGTH(content) >= 1 AND LENGTH(content) <= 1000"
            },
            {
                "name": "created_at",
                "type": "TEXT",
                "not_null": True,
                "default": "CURRENT_TIMESTAMP"
            }
        ],
        "primary_key": ["id", "post_id"],  # Composite primary key
        "indexes": [
            {"name": "idx_comments_post", "columns": ["post_id", "created_at"]},
            {"name": "idx_comments_parent", "columns": ["parent_comment_id"]}
        ]
    },
    
    # ─────────────────────────────────────────────────────────────
    # TABLE 4: Tags - Many-to-Many Junction Table
    # ─────────────────────────────────────────────────────────────
    "tags": {
        "table_name": "tags",
        "columns": [
            {
                "name": "id",
                "type": "INTEGER",
                "primary_key": True,
                "autoincrement": True
            },
            {
                "name": "name",
                "type": "TEXT",
                "not_null": True,
                "unique": True,
                "collate": "NOCASE"
            },
            {
                "name": "slug",
                "type": "TEXT",
                "not_null": True,
                "unique": True
            },
            {
                "name": "created_at",
                "type": "TEXT",
                "default": "CURRENT_TIMESTAMP"
            }
        ]
    },
    
    # ─────────────────────────────────────────────────────────────
    # TABLE 5: Post_Tags - Junction Table with Composite FK
    # ─────────────────────────────────────────────────────────────
    "post_tags": {
        "table_name": "post_tags",
        "columns": [
            {
                "name": "post_id",
                "type": "INTEGER",
                "not_null": True,
                "foreign_key": {
                    "table": "posts",
                    "column": "id",
                    "on_delete": "CASCADE"
                }
            },
            {
                "name": "tag_id",
                "type": "INTEGER",
                "not_null": True,
                "foreign_key": {
                    "table": "tags",
                    "column": "id",
                    "on_delete": "CASCADE"
                }
            },
            {
                "name": "added_at",
                "type": "TEXT",
                "default": "CURRENT_TIMESTAMP"
            }
        ],
        "primary_key": ["post_id", "tag_id"],  # Composite PK
        "indexes": [
            {"name": "idx_post_tags_tag", "columns": ["tag_id"]}
        ]
    },
    
    # ─────────────────────────────────────────────────────────────
    # TABLE 6: Settings - Generated Columns (SQLite 3.31+)
    # ─────────────────────────────────────────────────────────────
    "settings": {
        "table_name": "settings",
        "columns": [
            {
                "name": "id",
                "type": "INTEGER",
                "primary_key": True
            },
            {
                "name": "key",
                "type": "TEXT",
                "not_null": True,
                "unique": True
            },
            {
                "name": "value",
                "type": "TEXT"
            },
            {
                "name": "value_type",
                "type": "TEXT",
                "check": "value_type IN ('string', 'number', 'boolean', 'json')"
            },
            # Generated column (VIRTUAL) - computed on read
            {
                "name": "key_upper",
                "type": "TEXT",
                "generated": {
                    "expression": "UPPER(key)",
                    "stored": False  # VIRTUAL = not stored on disk
                }
            },
            # Generated column (STORED) - computed on write
            {
                "name": "value_length",
                "type": "INTEGER",
                "generated": {
                    "expression": "LENGTH(value)",
                    "stored": True  # STORED = saved to disk
                }
            },
            {
                "name": "created_at",
                "type": "TEXT",
                "default": "CURRENT_TIMESTAMP"
            }
        ],
        "indexes": [
            # Index on generated column
            {"name": "idx_settings_key_upper", "columns": ["key_upper"]}
        ]
    },
    
    # ─────────────────────────────────────────────────────────────
    # TABLE 7: Products - STRICT Type Enforcement (SQLite 3.37+)
    # ─────────────────────────────────────────────────────────────
    "products": {
        "table_name": "products",
        "columns": [
            {
                "name": "id",
                "type": "INTEGER",
                "primary_key": True
            },
            {
                "name": "sku",
                "type": "TEXT",
                "not_null": True,
                "unique": True
            },
            {
                "name": "name",
                "type": "TEXT",
                "not_null": True
            },
            {
                "name": "price",
                "type": "REAL",
                "not_null": True,
                "check": "price >= 0"
            },
            {
                "name": "stock",
                "type": "INTEGER",
                "not_null": True,
                "default": 0,
                "check": "stock >= 0"
            },
            {
                "name": "metadata",
                "type": "TEXT",  # JSON stored as TEXT
                "check": "json_valid(metadata)"  # SQLite JSON validation
            },
            {
                "name": "created_at",
                "type": "TEXT",
                "default": "CURRENT_TIMESTAMP"
            }
        ],
        "options": {
            "strict": True  # STRICT table - enforces type affinity
        },
        "indexes": [
            {"name": "idx_products_sku", "columns": ["sku"]},
            {"name": "idx_products_price", "columns": ["price"]},
            # Partial index for in-stock items
            {"name": "idx_products_in_stock", "columns": ["sku"], "where": "stock > 0"}
        ]
    },
    
    # ─────────────────────────────────────────────────────────────
    # TABLE 8: Sessions - WITHOUT ROWID Optimization
    # ─────────────────────────────────────────────────────────────
    "sessions": {
        "table_name": "sessions",
        "columns": [
            {
                "name": "session_id",
                "type": "TEXT",
                "primary_key": True  # Must have explicit PK for WITHOUT ROWID
            },
            {
                "name": "user_id",
                "type": "INTEGER",
                "not_null": True,
                "foreign_key": {
                    "table": "users",
                    "column": "id",
                    "on_delete": "CASCADE"
                }
            },
            {
                "name": "token",
                "type": "TEXT",
                "not_null": True
            },
            {
                "name": "expires_at",
                "type": "TEXT",
                "not_null": True
            },
            {
                "name": "created_at",
                "type": "TEXT",
                "default": "CURRENT_TIMESTAMP"
            }
        ],
        "options": {
            "without_rowid": True  # Optimization for tables with TEXT primary key
        },
        "indexes": [
            {"name": "idx_sessions_user", "columns": ["user_id"]},
            {"name": "idx_sessions_token", "columns": ["token"], "unique": True}
        ]
    },
    
    # ─────────────────────────────────────────────────────────────
    # TABLE 9: Audit_Log - All Foreign Key Actions Demonstrated
    # ─────────────────────────────────────────────────────────────
    "audit_log": {
        "table_name": "audit_log",
        "columns": [
            {
                "name": "id",
                "type": "INTEGER",
                "primary_key": True,
                "autoincrement": True
            },
            {
                "name": "user_id_cascade",
                "type": "INTEGER",
                "foreign_key": {
                    "table": "users",
                    "column": "id",
                    "on_delete": "CASCADE",    # Delete log when user deleted
                    "on_update": "CASCADE"
                }
            },
            {
                "name": "user_id_set_null",
                "type": "INTEGER",
                "foreign_key": {
                    "table": "users",
                    "column": "id",
                    "on_delete": "SET NULL",   # Keep log but nullify user
                    "on_update": "SET NULL"
                }
            },
            {
                "name": "user_id_restrict",
                "type": "INTEGER",
                "foreign_key": {
                    "table": "users",
                    "column": "id",
                    "on_delete": "RESTRICT",   # Prevent user deletion if logs exist
                    "on_update": "RESTRICT"
                }
            },
            {
                "name": "user_id_no_action",
                "type": "INTEGER",
                "foreign_key": {
                    "table": "users",
                    "column": "id",
                    "on_delete": "NO ACTION",  # Similar to RESTRICT but deferred
                    "on_update": "NO ACTION"
                }
            },
            {
                "name": "action",
                "type": "TEXT",
                "not_null": True
            },
            {
                "name": "details",
                "type": "TEXT"
            },
            {
                "name": "timestamp",
                "type": "TEXT",
                "not_null": True,
                "default": "CURRENT_TIMESTAMP"
            }
        ]
    },
    
    # ─────────────────────────────────────────────────────────────
    # TABLE 10: Documents - Full-Text Search (FTS5)
    # ─────────────────────────────────────────────────────────────
    "documents": {
        "table_name": "documents",
        "columns": [
            {
                "name": "id",
                "type": "INTEGER",
                "primary_key": True
            },
            {
                "name": "title",
                "type": "TEXT",
                "not_null": True
            },
            {
                "name": "content",
                "type": "TEXT",
                "not_null": True
            },
            {
                "name": "author_id",
                "type": "INTEGER",
                "foreign_key": {
                    "table": "users",
                    "column": "id",
                    "on_delete": "SET NULL"
                }
            },
            {
                "name": "created_at",
                "type": "TEXT",
                "default": "CURRENT_TIMESTAMP"
            }
        ]
    },
    
    # FTS5 Virtual Table for full-text search on documents
    "documents_fts": {
        "table_name": "documents_fts",
        "virtual_table": True,
        "using": "fts5",
        "columns": [
            {"name": "title", "type": "TEXT"},
            {"name": "content", "type": "TEXT"},
            {"name": "content_rowid", "type": "INTEGER", "unindexed": True}  # Reference to documents.id
        ],
        "fts_options": {
            "content": "documents",  # Source table
            "content_rowid": "id",   # Reference column
            "tokenize": "porter"     # Porter stemming algorithm
        }
    },
    
    # ─────────────────────────────────────────────────────────────
    # TABLE 11: Events - WITHOUT ROWID with Composite Key
    # ─────────────────────────────────────────────────────────────
    "events": {
        "table_name": "events",
        "columns": [
            {
                "name": "event_id",
                "type": "TEXT",
                "not_null": True
            },
            {
                "name": "timestamp",
                "type": "TEXT",
                "not_null": True
            },
            {
                "name": "user_id",
                "type": "INTEGER",
                "foreign_key": {
                    "table": "users",
                    "column": "id",
                    "on_delete": "CASCADE"
                }
            },
            {
                "name": "event_type",
                "type": "TEXT",
                "not_null": True
            },
            {
                "name": "data",
                "type": "TEXT"
            }
        ],
        "primary_key": ["event_id", "timestamp"],  # Composite PK required for WITHOUT ROWID
        "options": {
            "without_rowid": True  # More efficient for event logs
        },
        "indexes": [
            {"name": "idx_events_user", "columns": ["user_id", "timestamp"]},
            {"name": "idx_events_type", "columns": ["event_type"]}
        ]
    }
}

# ═══════════════════════════════════════════════════════════════════
# VIEWS - Derived/Computed Tables
# ═══════════════════════════════════════════════════════════════════

VIEWS = {
    # Simple view
    "active_users": {
        "name": "active_users",
        "sql": """
            CREATE VIEW active_users AS
            SELECT id, username, email, role, created_at
            FROM users
            WHERE is_active = 1 AND status = 'active'
        """
    },
    
    # Complex view with JOINs
    "user_post_stats": {
        "name": "user_post_stats",
        "sql": """
            CREATE VIEW user_post_stats AS
            SELECT 
                u.id,
                u.username,
                COUNT(p.id) as post_count,
                SUM(p.view_count) as total_views,
                MAX(p.created_at) as last_post_at
            FROM users u
            LEFT JOIN posts p ON u.id = p.user_id
            GROUP BY u.id, u.username
        """
    },
    
    # View with subquery
    "popular_posts": {
        "name": "popular_posts",
        "sql": """
            CREATE VIEW popular_posts AS
            SELECT 
                p.*,
                u.username as author,
                (SELECT COUNT(*) FROM comments c WHERE c.post_id = p.id) as comment_count
            FROM posts p
            JOIN users u ON p.user_id = u.id
            WHERE p.view_count > 100
            ORDER BY p.view_count DESC
        """
    }
}

# ═══════════════════════════════════════════════════════════════════
# TRIGGERS - Automated Actions on Data Changes
# ═══════════════════════════════════════════════════════════════════

TRIGGERS = {
    # Update timestamp on row update
    "users_update_timestamp": {
        "name": "users_update_timestamp",
        "table": "users",
        "when": "AFTER UPDATE",
        "for_each": "ROW",
        "sql": """
            CREATE TRIGGER users_update_timestamp
            AFTER UPDATE ON users
            FOR EACH ROW
            BEGIN
                UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END
        """
    },
    
    # Increment view count on post read
    "posts_increment_views": {
        "name": "posts_increment_views",
        "table": "posts",
        "when": "AFTER UPDATE",
        "sql": """
            CREATE TRIGGER posts_increment_views
            AFTER UPDATE OF view_count ON posts
            FOR EACH ROW
            WHEN NEW.view_count > OLD.view_count
            BEGIN
                -- Could log to audit_log here
                INSERT INTO audit_log (user_id_cascade, action, details, timestamp)
                VALUES (NULL, 'post_viewed', 'Post ID: ' || NEW.id, CURRENT_TIMESTAMP);
            END
        """
    },
    
    # Prevent deletion of users with posts (business logic)
    "users_prevent_delete_with_posts": {
        "name": "users_prevent_delete_with_posts",
        "table": "users",
        "when": "BEFORE DELETE",
        "sql": """
            CREATE TRIGGER users_prevent_delete_with_posts
            BEFORE DELETE ON users
            FOR EACH ROW
            WHEN (SELECT COUNT(*) FROM posts WHERE user_id = OLD.id) > 0
            BEGIN
                SELECT RAISE(ABORT, 'Cannot delete user with existing posts');
            END
        """
    },
    
    # Auto-create slug from name
    "tags_auto_slug": {
        "name": "tags_auto_slug",
        "table": "tags",
        "when": "BEFORE INSERT",
        "sql": """
            CREATE TRIGGER tags_auto_slug
            BEFORE INSERT ON tags
            FOR EACH ROW
            WHEN NEW.slug IS NULL
            BEGIN
                SELECT RAISE(IGNORE)
                WHERE NEW.slug IS NULL;
                UPDATE tags SET slug = LOWER(REPLACE(NEW.name, ' ', '-'))
                WHERE rowid = NEW.rowid;
            END
        """
    },
    
    # Sync FTS table when documents updated
    "documents_fts_sync_insert": {
        "name": "documents_fts_sync_insert",
        "table": "documents",
        "when": "AFTER INSERT",
        "sql": """
            CREATE TRIGGER documents_fts_sync_insert
            AFTER INSERT ON documents
            BEGIN
                INSERT INTO documents_fts(rowid, title, content)
                VALUES (NEW.id, NEW.title, NEW.content);
            END
        """
    },
    
    "documents_fts_sync_update": {
        "name": "documents_fts_sync_update",
        "table": "documents",
        "when": "AFTER UPDATE",
        "sql": """
            CREATE TRIGGER documents_fts_sync_update
            AFTER UPDATE ON documents
            BEGIN
                UPDATE documents_fts 
                SET title = NEW.title, content = NEW.content
                WHERE rowid = NEW.id;
            END
        """
    },
    
    "documents_fts_sync_delete": {
        "name": "documents_fts_sync_delete",
        "table": "documents",
        "when": "AFTER DELETE",
        "sql": """
            CREATE TRIGGER documents_fts_sync_delete
            AFTER DELETE ON documents
            BEGIN
                DELETE FROM documents_fts WHERE rowid = OLD.id;
            END
        """
    }
}

# ═══════════════════════════════════════════════════════════════════
# ADDITIONAL SQLITE FEATURES
# ═══════════════════════════════════════════════════════════════════

ADVANCED_FEATURES = {
    # ─────────────────────────────────────────────────────────────
    # Collation Sequences
    # ─────────────────────────────────────────────────────────────
    "collations": [
        "BINARY",     # Byte-by-byte comparison (default)
        "NOCASE",     # Case-insensitive for ASCII
        "RTRIM",      # Ignore trailing spaces
        # Can define custom collations via sqlite3.create_collation()
    ],
    
    # ─────────────────────────────────────────────────────────────
    # SQLite PRAGMA Settings
    # ─────────────────────────────────────────────────────────────
    "pragmas": {
        "foreign_keys": "ON",              # Enable foreign key constraints
        "journal_mode": "WAL",             # Write-Ahead Logging for better concurrency
        "synchronous": "NORMAL",           # Balance between safety and speed
        "cache_size": -64000,              # 64MB cache (negative = KB)
        "temp_store": "MEMORY",            # Store temp tables in memory
        "mmap_size": 268435456,            # 256MB memory-mapped I/O
        "page_size": 4096,                 # 4KB page size
        "auto_vacuum": "INCREMENTAL",      # Automatic space reclamation
        "encoding": "UTF-8"                # Character encoding
    },
    
    # ─────────────────────────────────────────────────────────────
    # Data Types - SQLite Type Affinity
    # ─────────────────────────────────────────────────────────────
    "type_affinity": {
        "INTEGER": ["INT", "INTEGER", "TINYINT", "SMALLINT", "MEDIUMINT", "BIGINT", 
                    "UNSIGNED BIG INT", "INT2", "INT8"],
        "TEXT": ["CHARACTER", "VARCHAR", "VARYING CHARACTER", "NCHAR", 
                 "NATIVE CHARACTER", "NVARCHAR", "TEXT", "CLOB"],
        "BLOB": ["BLOB"],
        "REAL": ["REAL", "DOUBLE", "DOUBLE PRECISION", "FLOAT"],
        "NUMERIC": ["NUMERIC", "DECIMAL", "BOOLEAN", "DATE", "DATETIME"]
    },
    
    # ─────────────────────────────────────────────────────────────
    # Constraint Types
    # ─────────────────────────────────────────────────────────────
    "constraints": {
        "column_level": [
            "PRIMARY KEY",
            "UNIQUE",
            "NOT NULL",
            "CHECK (expression)",
            "DEFAULT value",
            "COLLATE collation_name",
            "GENERATED ALWAYS AS (expression) STORED/VIRTUAL",
            "FOREIGN KEY REFERENCES table(column)"
        ],
        "table_level": [
            "PRIMARY KEY (col1, col2)",           # Composite PK
            "UNIQUE (col1, col2)",                # Composite unique
            "CHECK (expression)",                  # Table-level check
            "FOREIGN KEY (col) REFERENCES table(col) ON DELETE action"
        ]
    },
    
    # ─────────────────────────────────────────────────────────────
    # ALTER TABLE Support in SQLite
    # ─────────────────────────────────────────────────────────────
    "alter_table_support": {
        "sqlite_3_35_plus": {
            "ADD COLUMN": True,
            "DROP COLUMN": True,      # Requires SQLite 3.35+
            "RENAME COLUMN": True,    # Requires SQLite 3.25+
            "RENAME TABLE": True
        },
        "sqlite_pre_3_35": {
            "ADD COLUMN": True,
            "DROP COLUMN": False,     # Requires table recreation
            "RENAME COLUMN": False,   # Requires table recreation
            "RENAME TABLE": True,
            "ALTER COLUMN": False     # Never supported - requires table recreation
        },
        "workarounds": {
            "drop_column": "Table recreation pattern",
            "rename_column": "Table recreation pattern",
            "change_type": "Table recreation pattern",
            "add_constraint": "Table recreation pattern"
        }
    },
    
    # ─────────────────────────────────────────────────────────────
    # Index Types
    # ─────────────────────────────────────────────────────────────
    "index_types": [
        "Simple index: CREATE INDEX idx_name ON table(column)",
        "Composite index: CREATE INDEX idx_name ON table(col1, col2)",
        "Unique index: CREATE UNIQUE INDEX idx_name ON table(column)",
        "Partial index: CREATE INDEX idx_name ON table(column) WHERE condition",
        "Expression index: CREATE INDEX idx_name ON table(LOWER(column))",
        "Covering index: All columns in query are in index (auto-optimized)"
    ]
}

# ═══════════════════════════════════════════════════════════════════
# SQL GENERATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def generate_create_table_sql(table_def):
    """Generate CREATE TABLE statement from schema definition."""
    table_name = table_def["table_name"]
    columns = table_def["columns"]
    
    # Handle virtual tables (FTS, etc.)
    if table_def.get("virtual_table"):
        return generate_virtual_table_sql(table_def)
    
    column_defs = []
    foreign_keys = []
    
    for col in columns:
        # Skip generated columns for now (added separately)
        if "generated" in col:
            col_def = f"{col['name']} {col['type']} GENERATED ALWAYS AS ({col['generated']['expression']})"
            if col['generated'].get('stored'):
                col_def += " STORED"
            else:
                col_def += " VIRTUAL"
            column_defs.append(col_def)
            continue
        
        # Build column definition
        col_def = f"{col['name']} {col['type']}"
        
        if col.get("primary_key") and "primary_key" not in table_def:
            col_def += " PRIMARY KEY"
            if col.get("autoincrement"):
                col_def += " AUTOINCREMENT"
        
        if col.get("not_null"):
            col_def += " NOT NULL"
        
        if col.get("unique"):
            col_def += " UNIQUE"
        
        if "default" in col and col["default"] is not None:
            col_def += f" DEFAULT {col['default']}"
        
        if col.get("collate"):
            col_def += f" COLLATE {col['collate']}"
        
        if "check" in col:
            col_def += f" CHECK ({col['check']})"
        
        column_defs.append(col_def)
        
        # Handle foreign keys
        if "foreign_key" in col:
            fk = col["foreign_key"]
            fk_def = f"FOREIGN KEY ({col['name']}) REFERENCES {fk['table']}({fk['column']})"
            
            if "on_delete" in fk:
                fk_def += f" ON DELETE {fk['on_delete']}"
            if "on_update" in fk:
                fk_def += f" ON UPDATE {fk['on_update']}"
            
            foreign_keys.append(fk_def)
    
    # Add table-level primary key if composite
    if "primary_key" in table_def:
        pk_cols = ", ".join(table_def["primary_key"])
        column_defs.append(f"PRIMARY KEY ({pk_cols})")
    
    # Combine all definitions
    all_defs = column_defs + foreign_keys
    create_sql = f"CREATE TABLE {table_name} (\n  " + ",\n  ".join(all_defs) + "\n)"
    
    # Add table options
    options = table_def.get("options", {})
    if options.get("strict"):
        create_sql += " STRICT"
    if options.get("without_rowid"):
        create_sql += " WITHOUT ROWID"
    
    create_sql += ";"
    
    return create_sql

def generate_virtual_table_sql(table_def):
    """Generate CREATE VIRTUAL TABLE for FTS, etc."""
    table_name = table_def["table_name"]
    using = table_def["using"]
    
    if using == "fts5":
        # FTS5 table
        columns = table_def["columns"]
        col_names = []
        
        for col in columns:
            col_spec = col["name"]
            if col.get("unindexed"):
                col_spec += " UNINDEXED"
            col_names.append(col_spec)
        
        fts_opts = table_def.get("fts_options", {})
        if "content" in fts_opts:
            col_names.append(f"content={fts_opts['content']}")
        if "tokenize" in fts_opts:
            col_names.append(f"tokenize='{fts_opts['tokenize']}'")
        
        return f"CREATE VIRTUAL TABLE {table_name} USING fts5({', '.join(col_names)});"
    
    return ""

def generate_index_sql(table_name, index_def):
    """Generate CREATE INDEX statement."""
    index_name = index_def["name"]
    
    # Expression index
    if "expression" in index_def:
        sql = f"CREATE INDEX {index_name} ON {table_name}({index_def['expression']})"
    else:
        columns = ", ".join(index_def["columns"])
        unique = "UNIQUE " if index_def.get("unique") else ""
        sql = f"CREATE {unique}INDEX {index_name} ON {table_name}({columns})"
    
    # Partial index with WHERE clause
    if "where" in index_def:
        sql += f" WHERE {index_def['where']}"
    
    sql += ";"
    return sql

# ═══════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def create_database(db_path="test_complete.db"):
    """Create a complete SQLite database with all features."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Enable foreign keys
    cur.execute("PRAGMA foreign_keys = ON")
    
    # Set recommended PRAGMAs
    for pragma, value in ADVANCED_FEATURES["pragmas"].items():
        try:
            if isinstance(value, str):
                cur.execute(f"PRAGMA {pragma} = '{value}'")
            else:
                cur.execute(f"PRAGMA {pragma} = {value}")
        except Exception as e:
            # Some PRAGMAs are read-only or version-specific
            print(f"  Note: Could not set PRAGMA {pragma}: {e}")
    
    # Create tables
    for table_def in SCHEMA.values():
        sql = generate_create_table_sql(table_def)
        print(f"Creating table: {table_def['table_name']}")
        print(sql)
        print()
        cur.execute(sql)
    
    # Create indexes
    for table_def in SCHEMA.values():
        if "indexes" in table_def:
            for index_def in table_def["indexes"]:
                sql = generate_index_sql(table_def["table_name"], index_def)
                print(f"Creating index: {index_def['name']}")
                print(sql)
                print()
                cur.execute(sql)
    
    # Create views
    for view_def in VIEWS.values():
        print(f"Creating view: {view_def['name']}")
        print(view_def['sql'])
        print()
        cur.execute(view_def['sql'])
    
    # Create triggers
    for trigger_def in TRIGGERS.values():
        print(f"Creating trigger: {trigger_def['name']}")
        print(trigger_def['sql'])
        print()
        cur.execute(trigger_def['sql'])
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database created: {db_path}")
    print(f"   Tables: {len(SCHEMA)}")
    print(f"   Views: {len(VIEWS)}")
    print(f"   Triggers: {len(TRIGGERS)}")
    
    return db_path

def introspect_database(db_path):
    """Introspect existing SQLite database to show all features."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    print(f"\n{'='*60}")
    print(f"Database Introspection: {db_path}")
    print(f"{'='*60}\n")
    
    # Tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cur.fetchall()]
    print(f"Tables ({len(tables)}):")
    for table in tables:
        print(f"  • {table}")
        
        # Show table info
        cur.execute(f"PRAGMA table_info({table})")
        columns = cur.fetchall()
        for col in columns:
            cid, name, dtype, notnull, default, pk = col
            constraints = []
            if pk:
                constraints.append("PRIMARY KEY")
            if notnull:
                constraints.append("NOT NULL")
            if default is not None:
                constraints.append(f"DEFAULT {default}")
            
            constraint_str = " ".join(constraints) if constraints else ""
            print(f"    - {name}: {dtype} {constraint_str}")
        
        # Show foreign keys
        cur.execute(f"PRAGMA foreign_key_list({table})")
        fks = cur.fetchall()
        if fks:
            print(f"    Foreign Keys:")
            for fk in fks:
                id, seq, ref_table, from_col, to_col, on_update, on_delete, match = fk
                print(f"      {from_col} → {ref_table}.{to_col} (ON DELETE {on_delete}, ON UPDATE {on_update})")
        
        # Show indexes
        cur.execute(f"PRAGMA index_list({table})")
        indexes = cur.fetchall()
        if indexes:
            print(f"    Indexes:")
            for idx in indexes:
                seq, name, unique, origin, partial = idx
                unique_str = "UNIQUE " if unique else ""
                partial_str = " (PARTIAL)" if partial else ""
                print(f"      {unique_str}{name}{partial_str}")
        
        print()
    
    # Views
    cur.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")
    views = [row[0] for row in cur.fetchall()]
    if views:
        print(f"\nViews ({len(views)}):")
        for view in views:
            print(f"  • {view}")
    
    # Triggers
    cur.execute("SELECT name, tbl_name FROM sqlite_master WHERE type='trigger' ORDER BY name")
    triggers = cur.fetchall()
    if triggers:
        print(f"\nTriggers ({len(triggers)}):")
        for name, table in triggers:
            print(f"  • {name} (on {table})")
    
    conn.close()

def show_sqlite_version():
    """Show SQLite version and feature support."""
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()
    
    cur.execute("SELECT sqlite_version()")
    version = cur.fetchone()[0]
    
    print(f"\nSQLite Version: {version}")
    print(f"\nFeature Support:")
    
    # Check feature support
    features = {
        "Foreign Keys": "PRAGMA foreign_keys",
        "WAL Mode": "PRAGMA journal_mode",
        "STRICT tables": "3.37.0",  # Version check
        "DROP COLUMN": "3.35.0",
        "RENAME COLUMN": "3.25.0",
        "Generated Columns": "3.31.0",
        "Window Functions": "3.25.0",
        "UPSERT": "3.24.0",
        "FTS5": True  # Usually available
    }
    
    for feature, check in features.items():
        if isinstance(check, str) and check.startswith("PRAGMA"):
            cur.execute(check)
            value = cur.fetchone()[0]
            print(f"  • {feature}: {value}")
        elif isinstance(check, str):
            # Version comparison
            supported = tuple(map(int, version.split('.'))) >= tuple(map(int, check.split('.')))
            status = "✅" if supported else "❌"
            print(f"  • {feature}: {status} (requires {check}+)")
        else:
            print(f"  • {feature}: ✅")
    
    conn.close()

# ═══════════════════════════════════════════════════════════════════
# EXAMPLE USAGE & TESTS
# ═══════════════════════════════════════════════════════════════════

def example_usage():
    """Demonstrate schema creation and introspection."""
    print("SQLite Complete Schema Reference")
    print("="*60)
    
    # Show SQLite version and features
    show_sqlite_version()
    
    # Create database with all features
    print(f"\n{'='*60}")
    print("Creating Complete Database...")
    print(f"{'='*60}\n")
    
    db_path = create_database("test_complete.db")
    
    # Introspect the created database
    introspect_database(db_path)
    
    # Show sample data insertion
    print(f"\n{'='*60}")
    print("Sample Data Operations")
    print(f"{'='*60}\n")
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Insert user
    cur.execute("""
        INSERT INTO users (username, email, password_hash, role, age, rating)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ["john_doe", "john@example.com", "hashed_password", "admin", 30, 4.5])
    
    user_id = cur.lastrowid
    print(f"✅ Created user with ID: {user_id}")
    
    # Insert post
    cur.execute("""
        INSERT INTO posts (user_id, title, content)
        VALUES (?, ?, ?)
    """, [user_id, "My First Post", "This is the content of my first post."])
    
    post_id = cur.lastrowid
    print(f"✅ Created post with ID: {post_id}")
    
    # Query view
    cur.execute("SELECT * FROM user_post_stats WHERE username = ?", ["john_doe"])
    stats = cur.fetchone()
    print(f"✅ User stats: {stats}")
    
    conn.commit()
    conn.close()
    
    print(f"\n{'='*60}")
    print("Complete! Database ready for inspection.")
    print(f"{'='*60}")

# ═══════════════════════════════════════════════════════════════════
# REFERENCE DOCUMENTATION
# ═══════════════════════════════════════════════════════════════════

REFERENCE = """
SQLite Complete Feature Reference
===================================

1. DATA TYPES (Type Affinity):
   - INTEGER: Whole numbers, up to 8 bytes
   - TEXT: UTF-8, UTF-16BE, or UTF-16LE strings
   - BLOB: Binary large object, stored exactly as input
   - REAL: Floating point, 8-byte IEEE floating point
   - NUMERIC: Flexible numeric storage

2. CONSTRAINTS:
   - PRIMARY KEY: Unique identifier (can be composite)
   - FOREIGN KEY: References another table (with ON DELETE/UPDATE actions)
   - UNIQUE: No duplicate values (can be composite)
   - NOT NULL: Column must have a value
   - CHECK: Custom validation expression
   - DEFAULT: Default value if not provided

3. FOREIGN KEY ACTIONS:
   - CASCADE: Delete/update child rows when parent changes
   - RESTRICT: Prevent parent change if children exist
   - SET NULL: Set child FK to NULL when parent deleted
   - SET DEFAULT: Set child FK to default when parent deleted
   - NO ACTION: Similar to RESTRICT but deferred to end of transaction

4. INDEXES:
   - Simple: Single column
   - Composite: Multiple columns
   - Unique: Enforces uniqueness
   - Partial: With WHERE clause for selective indexing
   - Expression: On computed expressions like LOWER(column)

5. GENERATED COLUMNS (SQLite 3.31+):
   - VIRTUAL: Computed on read, not stored
   - STORED: Computed on write, saved to disk

6. SPECIAL TABLE TYPES:
   - STRICT: Enforces type checking (SQLite 3.37+)
   - WITHOUT ROWID: Optimization for tables with specific PK patterns
   - Virtual Tables: FTS5 (full-text search), R-Tree, etc.

7. TRIGGERS:
   - BEFORE INSERT/UPDATE/DELETE: Execute before operation
   - AFTER INSERT/UPDATE/DELETE: Execute after operation
   - INSTEAD OF: For views, replace default action

8. VIEWS:
   - Simple: SELECT from one table
   - Complex: JOINs, aggregations, subqueries
   - Updatable: With INSTEAD OF triggers

9. ALTER TABLE Support:
   SQLite 3.35+:
   - ADD COLUMN ✅
   - DROP COLUMN ✅
   - RENAME COLUMN ✅
   - RENAME TABLE ✅
   
   NOT Supported:
   - ALTER COLUMN (type, constraints) ❌ → Requires table recreation
   - ADD CONSTRAINT ❌ → Requires table recreation

10. PRAGMAS (Database Configuration):
    - foreign_keys: Enable/disable FK constraints
    - journal_mode: DELETE, TRUNCATE, PERSIST, MEMORY, WAL, OFF
    - synchronous: OFF, NORMAL, FULL, EXTRA
    - cache_size: Memory cache size
    - temp_store: MEMORY, FILE, DEFAULT
    - auto_vacuum: NONE, FULL, INCREMENTAL

For complete documentation: https://www.sqlite.org/lang.html
"""

# ═══════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--create":
        # Create database and run examples
        example_usage()
    elif len(sys.argv) > 1 and sys.argv[1] == "--introspect":
        # Introspect existing database
        db_path = sys.argv[2] if len(sys.argv) > 2 else "test_complete.db"
        introspect_database(db_path)
    elif len(sys.argv) > 1 and sys.argv[1] == "--version":
        # Show SQLite version and features
        show_sqlite_version()
    elif len(sys.argv) > 1 and sys.argv[1] == "--reference":
        # Show reference documentation
        print(REFERENCE)
    else:
        # Show available commands
        print("SQLite Complete Schema Reference")
        print("="*60)
        print("\nUsage:")
        print("  python schema_sqlite_complete.py --create      # Create demo database")
        print("  python schema_sqlite_complete.py --introspect  # Introspect database")
        print("  python schema_sqlite_complete.py --version     # Show SQLite features")
        print("  python schema_sqlite_complete.py --reference   # Show documentation")
        print("\nThis schema demonstrates ALL SQLite features:")
        print(f"  • {len(SCHEMA)} tables with various configurations")
        print(f"  • {len(VIEWS)} views (simple and complex)")
        print(f"  • {len(TRIGGERS)} triggers (automation)")
        print("  • All data types (INTEGER, TEXT, REAL, BLOB, NUMERIC)")
        print("  • All constraints (PK, FK, UNIQUE, NOT NULL, CHECK, DEFAULT)")
        print("  • All FK actions (CASCADE, RESTRICT, SET NULL, NO ACTION)")
        print("  • Generated columns (VIRTUAL, STORED)")
        print("  • All index types (simple, composite, unique, partial, expression)")
        print("  • STRICT tables, WITHOUT ROWID, FTS5")
        print("  • Self-referencing FKs, composite keys")
        print("\nUse this as reference for migration system design!")

