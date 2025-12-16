#!/bin/bash
echo "🗑️  Deleting old database..."
rm -f test.db
echo "✅ Database deleted"
echo ""
echo "🚀 Initializing new database..."
python init_db_complete.py
echo ""
echo "✅ All done! You can now run: python main.py"
