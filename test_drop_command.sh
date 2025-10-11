#!/bin/bash
# Test DROP command across all three adapters

echo "════════════════════════════════════════════════════════════"
echo "Testing DROP TABLE Command Across All Adapters"
echo "════════════════════════════════════════════════════════════"

source venv/bin/activate

echo ""
echo "─────────────────────────────────────────────────────────────"
echo "Test 1: CSV Adapter"
echo "─────────────────────────────────────────────────────────────"
zolo shell << 'EOF'
data create --model @.zCLI.Schemas.zSchema.csv_demo
data drop users --model @.zCLI.Schemas.zSchema.csv_demo
exit
EOF

echo ""
echo "Verify: users.csv should be deleted"
ls -la tests/zData_tests/csv_demo/

echo ""
echo "─────────────────────────────────────────────────────────────"
echo "Test 2: SQLite Adapter"
echo "─────────────────────────────────────────────────────────────"
zolo shell << 'EOF'
data create --model @.zCLI.Schemas.zSchema.sqlite_demo
data drop users --model @.zCLI.Schemas.zSchema.sqlite_demo
exit
EOF

echo ""
echo "Verify: users table should be gone from demo.db"
sqlite3 tests/zData_tests/sqlite_demo/demo.db ".tables"

echo ""
echo "─────────────────────────────────────────────────────────────"
echo "Test 3: PostgreSQL Adapter"
echo "─────────────────────────────────────────────────────────────"
zolo shell << 'EOF'
data create --model @.zCLI.Schemas.zSchema.postgresql_demo
data drop users --model @.zCLI.Schemas.zSchema.postgresql_demo
exit
EOF

echo ""
echo "Verify: users table should be gone from demo database"
psql demo -c "\\dt"

echo ""
echo "Check .pginfo.yaml updated:"
cat tests/zData_tests/postgresql_demo/.pginfo.yaml

echo ""
echo "════════════════════════════════════════════════════════════"
echo "✅ DROP command tests complete!"
echo "════════════════════════════════════════════════════════════"

