#!/usr/bin/env python3
"""Quick script to import existing course data"""

import sys
from database import DatabaseManager

db = DatabaseManager()
db.initialize()

# Get filename from command line argument or use default
filename = sys.argv[1] if len(sys.argv) > 1 else 'courses_with_language.jsonl'

# Import the JSONL file
db.import_from_jsonl(filename)

# Show stats
stats = db.get_statistics()
print(f'\n✓ Database now has {stats["total_courses"]} courses')
print(f'✓ Total lessons: {stats["total_lessons"]}')
print(f'✓ Languages: {len(stats["by_language"])}')

db.close()
