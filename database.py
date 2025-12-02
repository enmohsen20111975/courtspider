#!/usr/bin/env python3
"""
Database Manager for CourseSpider
Manages SQLite database for efficient querying
"""

import sqlite3
import json
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime


class DatabaseManager:
    def __init__(self, db_path: str = 'data/courses.db'):
        self.db_path = db_path
        self.conn = None
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    def initialize(self):
        """Initialize database connection and create tables"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        print('✓ Connected to SQLite database')
        self.create_tables()
    
    def create_tables(self):
        """Create database tables"""
        cursor = self.conn.cursor()
        
        # Create courses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                youtube_id TEXT UNIQUE NOT NULL,
                url TEXT NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT,
                title TEXT NOT NULL,
                description TEXT,
                author_name TEXT,
                author_channel_id TEXT,
                author_homepage TEXT,
                author_subscribers INTEGER DEFAULT 0,
                duration_min INTEGER DEFAULT 0,
                lesson_count INTEGER DEFAULT 0,
                language TEXT NOT NULL,
                language_name TEXT NOT NULL,
                thumbnail TEXT,
                published_at TEXT,
                last_updated TEXT,
                verified_free INTEGER DEFAULT 1,
                scraped_at TEXT,
                tags TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create lessons table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                idx INTEGER NOT NULL,
                title TEXT NOT NULL,
                video_id TEXT NOT NULL,
                duration_min INTEGER DEFAULT 0,
                description TEXT,
                thumbnail TEXT,
                published_at TEXT,
                view_count INTEGER DEFAULT 0,
                like_count INTEGER DEFAULT 0,
                FOREIGN KEY (course_id) REFERENCES courses (id) ON DELETE CASCADE
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_courses_category ON courses(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_courses_language ON courses(language)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_courses_subcategory ON courses(subcategory)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_lessons_course_id ON lessons(course_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_courses_youtube_id ON courses(youtube_id)')
        
        self.conn.commit()
        print('✓ Database tables created/verified')
    
    def import_from_jsonl(self, filepath: str) -> Tuple[int, int]:
        """Import courses from JSONL file"""
        print(f"\nImporting courses from {filepath}...")
        
        imported = 0
        skipped = 0
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    course = json.loads(line)
                    if self.insert_course(course):
                        imported += 1
                    else:
                        skipped += 1
                except Exception as e:
                    print(f"Error importing course: {e}")
                    skipped += 1
        
        print(f"✓ Imported {imported} courses, skipped {skipped} duplicates")
        return imported, skipped
    
    def insert_course(self, course: Dict) -> bool:
        """Insert a single course with its lessons"""
        cursor = self.conn.cursor()
        
        # Check if course already exists
        cursor.execute('SELECT id FROM courses WHERE youtube_id = ?', (course['youtube_id'],))
        if cursor.fetchone():
            return False  # Course already exists
        
        # Insert course
        cursor.execute('''
            INSERT INTO courses (
                youtube_id, url, category, subcategory, title, description,
                author_name, author_channel_id, author_homepage, author_subscribers,
                duration_min, lesson_count, language, language_name, thumbnail,
                published_at, last_updated, verified_free, scraped_at, tags
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            course['youtube_id'],
            course['url'],
            course['category'],
            course.get('subcategory', course['category']),
            course['title'],
            course.get('description', ''),
            course['author'].get('name', 'Unknown'),
            course['author'].get('channel_id', ''),
            course['author'].get('homepage', ''),
            course['author'].get('subscribers', 0),
            course.get('duration_min', 0),
            course.get('lesson_count', 0),
            course.get('language', 'en'),
            course.get('language_name', 'English'),
            course.get('thumbnail', ''),
            course.get('published_at', datetime.utcnow().isoformat()),
            course.get('last_updated', datetime.utcnow().isoformat()),
            1 if course.get('verified_free', True) else 0,
            course.get('scraped_at', datetime.utcnow().isoformat()),
            json.dumps(course.get('tags', []))
        ))
        
        course_id = cursor.lastrowid
        
        # Insert lessons
        if 'lessons' in course and course['lessons']:
            for lesson in course['lessons']:
                cursor.execute('''
                    INSERT INTO lessons (
                        course_id, idx, title, video_id, duration_min, description,
                        thumbnail, published_at, view_count, like_count
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    course_id,
                    lesson['idx'],
                    lesson['title'],
                    lesson['video_id'],
                    lesson.get('duration_min', 0),
                    lesson.get('description', ''),
                    lesson.get('thumbnail', ''),
                    lesson.get('published_at', datetime.utcnow().isoformat()),
                    lesson.get('view_count', 0),
                    lesson.get('like_count', 0)
                ))
        
        self.conn.commit()
        return True
    
    def search_courses(self, filters: Dict) -> List[Dict]:
        """Search courses with filters"""
        query = '''
            SELECT c.*
            FROM courses c
            WHERE 1=1
        '''
        params = []
        
        if filters.get('category'):
            query += ' AND c.category = ?'
            params.append(filters['category'])
        
        if filters.get('subcategory'):
            query += ' AND c.subcategory = ?'
            params.append(filters['subcategory'])
        
        if filters.get('language'):
            query += ' AND c.language = ?'
            params.append(filters['language'])
        
        if filters.get('language_name'):
            query += ' AND c.language_name = ?'
            params.append(filters['language_name'])
        
        if filters.get('author'):
            query += ' AND c.author_name LIKE ?'
            params.append(f"%{filters['author']}%")
        
        if filters.get('search'):
            query += ' AND (c.title LIKE ? OR c.description LIKE ?)'
            params.extend([f"%{filters['search']}%", f"%{filters['search']}%"])
        
        if filters.get('min_lessons'):
            query += ' AND c.lesson_count >= ?'
            params.append(filters['min_lessons'])
        
        if filters.get('max_duration'):
            query += ' AND c.duration_min <= ?'
            params.append(filters['max_duration'])
        
        if filters.get('min_duration'):
            query += ' AND c.duration_min >= ?'
            params.append(filters['min_duration'])
        
        # Sorting
        sort_by = filters.get('sort', 'created_at')
        sort_order = filters.get('order', 'DESC')
        query += f' ORDER BY c.{sort_by} {sort_order}'
        
        # Pagination
        limit = min(int(filters.get('limit', 20)), 100)
        offset = int(filters.get('offset', 0))
        query += ' LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        
        courses = []
        for row in cursor.fetchall():
            course = dict(row)
            try:
                course['tags'] = json.loads(course['tags']) if course['tags'] else []
            except:
                course['tags'] = []
            courses.append(course)
        
        return courses
    
    def get_course_by_id(self, course_id: int) -> Optional[Dict]:
        """Get course by ID with lessons"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM courses WHERE id = ?', (course_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        course = dict(row)
        
        # Get lessons
        cursor.execute('SELECT * FROM lessons WHERE course_id = ? ORDER BY idx', (course_id,))
        course['lessons'] = [dict(r) for r in cursor.fetchall()]
        
        try:
            course['tags'] = json.loads(course['tags']) if course['tags'] else []
        except:
            course['tags'] = []
        
        return course
    
    def get_course_by_youtube_id(self, youtube_id: str) -> Optional[Dict]:
        """Get course by YouTube ID"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM courses WHERE youtube_id = ?', (youtube_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        course = dict(row)
        
        # Get lessons
        cursor.execute('SELECT * FROM lessons WHERE course_id = ? ORDER BY idx', (course['id'],))
        course['lessons'] = [dict(r) for r in cursor.fetchall()]
        
        try:
            course['tags'] = json.loads(course['tags']) if course['tags'] else []
        except:
            course['tags'] = []
        
        return course
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        cursor = self.conn.cursor()
        stats = {}
        
        # Total courses
        cursor.execute('SELECT COUNT(*) as total FROM courses')
        stats['total_courses'] = cursor.fetchone()['total']
        
        # By category
        cursor.execute('SELECT category, COUNT(*) as count FROM courses GROUP BY category')
        stats['by_category'] = {row['category']: row['count'] for row in cursor.fetchall()}
        
        # By language
        cursor.execute('SELECT language_name, COUNT(*) as count FROM courses GROUP BY language_name')
        stats['by_language'] = {row['language_name']: row['count'] for row in cursor.fetchall()}
        
        # Total lessons
        cursor.execute('SELECT SUM(lesson_count) as total FROM courses')
        stats['total_lessons'] = cursor.fetchone()['total'] or 0
        
        # Total duration
        cursor.execute('SELECT SUM(duration_min) as total FROM courses')
        total_minutes = cursor.fetchone()['total'] or 0
        stats['total_duration_hours'] = round(total_minutes / 60)
        
        return stats
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print('✓ Database connection closed')


if __name__ == '__main__':
    import glob
    
    db_manager = DatabaseManager()
    db_manager.initialize()
    
    # Import all JSONL files from data directory
    jsonl_files = glob.glob('data/*.jsonl')
    
    if not jsonl_files:
        print('No JSONL files found in data directory')
    else:
        for file in jsonl_files:
            db_manager.import_from_jsonl(file)
        
        # Print statistics
        stats = db_manager.get_statistics()
        print('\n' + '=' * 60)
        print('Database Statistics')
        print('=' * 60)
        print(f"Total Courses: {stats['total_courses']}")
        print(f"Total Lessons: {stats['total_lessons']}")
        print(f"Total Duration: {stats['total_duration_hours']} hours")
        print('\nBy Category:')
        for cat, count in stats['by_category'].items():
            print(f"  {cat}: {count}")
        print('\nBy Language:')
        for lang, count in stats['by_language'].items():
            print(f"  {lang}: {count}")
        print('=' * 60)
    
    db_manager.close()
