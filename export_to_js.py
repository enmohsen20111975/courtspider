#!/usr/bin/env python3
"""
Export SQLite database to JavaScript file for standalone web app
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path


def export_database_to_js(db_path='data/courses.db', output_path='standalone/courses-data.js'):
    """Export entire database to JavaScript file"""
    
    print(f"\n{'='*60}")
    print("Exporting Database to JavaScript")
    print(f"{'='*60}\n")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all courses
    cursor.execute('''
        SELECT * FROM courses
        ORDER BY created_at DESC
    ''')
    
    courses_data = []
    total_lessons = 0
    categories = set()
    languages = set()
    
    for course_row in cursor.fetchall():
        course = dict(course_row)
        
        # Get lessons for this course
        cursor.execute('''
            SELECT * FROM lessons
            WHERE course_id = ?
            ORDER BY idx
        ''', (course['id'],))
        
        lessons = [dict(row) for row in cursor.fetchall()]
        total_lessons += len(lessons)
        
        # Add to sets
        categories.add(course['category'])
        languages.add(course['language_name'])
        
        # Build course object
        course_obj = {
            'id': course['id'],
            'youtube_id': course['youtube_id'],
            'url': course['url'],
            'title': course['title'],
            'description': course['description'] or '',
            'category': course['category'],
            'subcategory': course['subcategory'],
            'author_name': course['author_name'],
            'author_channel_id': course['author_channel_id'],
            'author_homepage': course['author_homepage'],
            'author_subscribers': course['author_subscribers'],
            'thumbnail': course['thumbnail'],
            'duration_min': course['duration_min'],
            'lesson_count': course['lesson_count'],
            'language': course['language'],
            'language_name': course['language_name'],
            'published_at': course['published_at'],
            'lessons': [
                {
                    'idx': lesson['idx'],
                    'title': lesson['title'],
                    'video_id': lesson['video_id'],
                    'duration_min': lesson['duration_min'],
                    'description': lesson['description'] or '',
                    'thumbnail': lesson['thumbnail'],
                    'view_count': lesson['view_count'],
                    'like_count': lesson['like_count']
                }
                for lesson in lessons
            ]
        }
        
        courses_data.append(course_obj)
    
    # Calculate total hours
    cursor.execute('SELECT SUM(duration_min) FROM courses')
    total_minutes = cursor.fetchone()[0] or 0
    total_hours = round(total_minutes / 60)
    
    # Create JavaScript file
    js_content = f'''// Auto-generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
// Total courses: {len(courses_data)}
// Total lessons: {total_lessons}
// Total hours: {total_hours}

const COURSES_DATA = {{
    stats: {{
        total_courses: {len(courses_data)},
        total_lessons: {total_lessons},
        total_hours: {total_hours},
        categories: {json.dumps(sorted(categories))},
        languages: {json.dumps(sorted(languages))},
        last_updated: "{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"
    }},
    courses: {json.dumps(courses_data, indent=2, ensure_ascii=False)}
}};
'''
    
    # Write to file
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    # Print statistics
    print(f"✓ Exported {len(courses_data)} courses")
    print(f"✓ Total lessons: {total_lessons:,}")
    print(f"✓ Total hours: {total_hours:,}")
    print(f"✓ Categories: {len(categories)}")
    print(f"✓ Languages: {len(languages)}")
    print(f"\n✓ JavaScript file created: {output_file}")
    print(f"  File size: {output_file.stat().st_size / 1024 / 1024:.2f} MB")
    
    print(f"\n{'='*60}")
    print("Export Complete!")
    print(f"{'='*60}\n")
    print("To use the standalone web app:")
    print("1. Copy standalone/index.html to your website")
    print("2. Copy standalone/courses-data.js to your website")
    print("3. Open index.html in a browser - no server needed!")
    print(f"{'='*60}\n")
    
    conn.close()


if __name__ == '__main__':
    export_database_to_js()
