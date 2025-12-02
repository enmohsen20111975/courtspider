#!/usr/bin/env python3
"""Import JSONL file to database"""

from database import DatabaseManager
import sys

if __name__ == '__main__':
    filepath = sys.argv[1] if len(sys.argv) > 1 else 'data/courses_2025-12-02_121420.jsonl'
    
    db = DatabaseManager()
    db.initialize()
    
    imported, skipped = db.import_from_jsonl(filepath)
    
    print(f'\nImported: {imported}')
    print(f'Skipped duplicates: {skipped}')
    
    stats = db.get_statistics()
    print(f'\nTotal courses in database: {stats["total_courses"]}')
    print(f'Total lessons in database: {stats["total_lessons"]}')
    
    db.close()
