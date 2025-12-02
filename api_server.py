#!/usr/bin/env python3
"""
Enhanced REST API for CourseSpider
Provides advanced filtering and search capabilities
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from database import DatabaseManager
from collector import EnhancedCourseCollector
import os
import threading
import uuid
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Initialize database
db = DatabaseManager()
db.initialize()

# Collection jobs tracking
collection_jobs = {}

@app.route('/api/courses', methods=['GET'])
def get_courses():
    """Search and filter courses"""
    try:
        filters = {
            'category': request.args.get('category'),
            'subcategory': request.args.get('subcategory'),
            'language': request.args.get('language'),
            'language_name': request.args.get('language_name'),
            'author': request.args.get('author'),
            'search': request.args.get('search') or request.args.get('q'),
            'min_lessons': request.args.get('min_lessons'),
            'max_duration': request.args.get('max_duration'),
            'min_duration': request.args.get('min_duration'),
            'sort': request.args.get('sort', 'created_at'),
            'order': request.args.get('order', 'DESC'),
            'limit': min(int(request.args.get('limit', 20)), 100),
            'offset': int(request.args.get('offset', 0))
        }
        
        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}
        
        courses = db.search_courses(filters)
        
        # Get total count for pagination
        total_filters = {k: v for k, v in filters.items() if k not in ['limit', 'offset', 'sort', 'order']}
        total_filters['limit'] = 999999
        total_filters['offset'] = 0
        all_results = db.search_courses(total_filters)
        total = len(all_results)
        
        return jsonify({
            'success': True,
            'data': courses,
            'pagination': {
                'limit': filters.get('limit', 20),
                'offset': filters.get('offset', 0),
                'total': total,
                'page': (filters.get('offset', 0) // filters.get('limit', 20)) + 1,
                'total_pages': (total + filters.get('limit', 20) - 1) // filters.get('limit', 20)
            },
            'filters': filters
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/courses/<int:course_id>', methods=['GET'])
def get_course_by_id(course_id):
    """Get specific course by database ID"""
    try:
        course = db.get_course_by_id(course_id)
        
        if not course:
            return jsonify({'success': False, 'error': 'Course not found'}), 404
        
        return jsonify({'success': True, 'data': course})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/courses/youtube/<youtube_id>', methods=['GET'])
def get_course_by_youtube_id(youtube_id):
    """Get course by YouTube playlist ID"""
    try:
        course = db.get_course_by_youtube_id(youtube_id)
        
        if not course:
            return jsonify({'success': False, 'error': 'Course not found'}), 404
        
        return jsonify({'success': True, 'data': course})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all categories with counts"""
    try:
        stats = db.get_statistics()
        categories = [{'name': name, 'count': count} 
                     for name, count in stats['by_category'].items()]
        return jsonify({'success': True, 'data': categories})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/languages', methods=['GET'])
def get_languages():
    """Get all languages with counts"""
    try:
        stats = db.get_statistics()
        languages = [{'name': name, 'count': count} 
                    for name, count in stats['by_language'].items()]
        return jsonify({'success': True, 'data': languages})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get database statistics"""
    try:
        stats = db.get_statistics()
        return jsonify({'success': True, 'data': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/search', methods=['POST'])
def advanced_search():
    """Advanced search with multiple filters"""
    try:
        data = request.get_json()
        
        query = data.get('query')
        categories = data.get('categories', [])
        languages = data.get('languages', [])
        min_lessons = data.get('min_lessons')
        max_lessons = data.get('max_lessons')
        min_duration = data.get('min_duration')
        max_duration = data.get('max_duration')
        authors = data.get('authors', [])
        tags = data.get('tags', [])
        sort = data.get('sort', 'created_at')
        order = data.get('order', 'DESC')
        limit = min(int(data.get('limit', 20)), 100)
        offset = int(data.get('offset', 0))
        
        filters = {
            'search': query,
            'min_lessons': min_lessons,
            'max_duration': max_duration,
            'min_duration': min_duration,
            'sort': sort,
            'order': order,
            'limit': 999999,  # Get all first, then filter
            'offset': 0
        }
        
        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}
        
        courses = db.search_courses(filters)
        
        # Additional filtering
        if categories:
            courses = [c for c in courses if c['category'] in categories]
        
        if languages:
            courses = [c for c in courses if c['language'] in languages]
        
        if authors:
            courses = [c for c in courses if any(
                author.lower() in c['author_name'].lower() for author in authors
            )]
        
        if tags:
            courses = [c for c in courses if any(
                tag in c.get('tags', []) for tag in tags
            )]
        
        # Apply pagination
        total = len(courses)
        courses = courses[offset:offset+limit]
        
        return jsonify({
            'success': True,
            'data': courses,
            'total': total,
            'query': data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'database': 'connected',
        'timestamp': str(__import__('datetime').datetime.utcnow())
    })


@app.route('/api/filters', methods=['GET'])
def get_filters():
    """Get all available filter options"""
    try:
        stats = db.get_statistics()
        return jsonify({
            'success': True,
            'data': {
                'categories': list(stats['by_category'].keys()),
                'languages': list(stats['by_language'].keys()),
                'total_courses': stats['total_courses']
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/courses/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    """Delete a course by ID"""
    try:
        # Get course first to check if exists
        course = db.get_course_by_id(course_id)
        if not course:
            return jsonify({'success': False, 'error': 'Course not found'}), 404
        
        # Delete from database
        db.conn.execute('DELETE FROM courses WHERE id = ?', (course_id,))
        db.conn.commit()
        
        return jsonify({
            'success': True,
            'message': f'Course {course_id} deleted successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/collect', methods=['POST'])
def start_collection():
    """Start a new collection job"""
    try:
        data = request.get_json() or {}
        courses_per_category = data.get('courses_per_category', 5)
        categories = data.get('categories', [])
        language = data.get('language', None)
        custom_keywords = data.get('custom_keywords', [])
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Initialize job status
        collection_jobs[job_id] = {
            'id': job_id,
            'status': 'running',
            'collected': 0,
            'total': (len(categories) + len(custom_keywords)) * courses_per_category,
            'logs': [],
            'started_at': datetime.utcnow().isoformat(),
            'error': None,
            'language': language,
            'custom_keywords': custom_keywords
        }
        
        # Start collection in background thread
        thread = threading.Thread(
            target=run_collection,
            args=(job_id, courses_per_category, categories)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': 'Collection started'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/collect/status/<job_id>', methods=['GET'])
def get_collection_status(job_id):
    """Get status of a collection job"""
    if job_id not in collection_jobs:
        return jsonify({'success': False, 'error': 'Job not found'}), 404
    
    return jsonify({
        'success': True,
        'status': collection_jobs[job_id]
    })


def run_collection(job_id, courses_per_category, categories):
    """Run collection process in background"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('YOUTUBE_API_KEY')
        if not api_key:
            collection_jobs[job_id]['status'] = 'failed'
            collection_jobs[job_id]['error'] = 'YouTube API key not found'
            return
        
        collector = EnhancedCourseCollector(api_key)
        collected_courses = []
        
        # Get language and custom keywords from request (if provided)
        language_filter = collection_jobs[job_id].get('language')
        custom_keywords = collection_jobs[job_id].get('custom_keywords', [])
        
        # Process custom keywords first
        if custom_keywords:
            collection_jobs[job_id]['logs'].append(f'Processing {len(custom_keywords)} custom keywords...')
            for keyword in custom_keywords:
                collection_jobs[job_id]['logs'].append(f'Searching: "{keyword}"')
                playlists = collector.search_playlists(keyword, 10, language_filter)
                
                for playlist in playlists[:courses_per_category]:
                    try:
                        course = collector.process_playlist(playlist, 'Custom')
                        if course:
                            collected_courses.append(course)
                            collection_jobs[job_id]['collected'] = len(collected_courses)
                            collection_jobs[job_id]['logs'].append(
                                f'✓ {course["title"][:50]}...'
                            )
                    except Exception as e:
                        collection_jobs[job_id]['logs'].append(f'✗ Error: {str(e)}')
        
        # Process standard categories
        for category in categories:
            if category not in collector.search_keywords:
                continue
            
            collection_jobs[job_id]['logs'].append(f'Collecting {category}...')
            keywords = collector.search_keywords[category]
            category_courses = []
            
            for keyword in keywords:
                if len(category_courses) >= courses_per_category:
                    break
                
                playlists = collector.search_playlists(keyword, 10, language_filter)
                
                for playlist in playlists:
                    if len(category_courses) >= courses_per_category:
                        break
                    
                    try:
                        course = collector.process_playlist(playlist, category)
                        if course:
                            category_courses.append(course)
                            collected_courses.append(course)
                            collection_jobs[job_id]['collected'] = len(collected_courses)
                            collection_jobs[job_id]['logs'].append(
                                f'✓ {course["title"][:50]}...'
                            )
                    except Exception as e:
                        collection_jobs[job_id]['logs'].append(f'✗ Error: {str(e)}')
        
        # Save to database
        if collected_courses:
            # Save to JSONL first (temporary)
            filename = f'courses_{datetime.now().strftime("%Y-%m-%d_%H%M%S")}.jsonl'
            filepath = os.path.join('data', filename)
            collector.save_courses(collected_courses, filename)
            
            collection_jobs[job_id]['logs'].append('Importing to database...')
            
            # Import to database with deduplication
            imported, skipped = db.import_from_jsonl(filepath)
            
            collection_jobs[job_id]['logs'].append(
                f'✅ Imported {imported} new courses, skipped {skipped} duplicates'
            )
            
            # Delete JSONL file after successful import
            try:
                os.remove(filepath)
                collection_jobs[job_id]['logs'].append('✓ Cleaned up temporary files')
            except Exception as e:
                collection_jobs[job_id]['logs'].append(f'⚠ Could not delete {filename}: {str(e)}')
            
            collection_jobs[job_id]['status'] = 'completed'
            collection_jobs[job_id]['logs'].append(
                f'✅ Completed! Total in database after deduplication: {imported} new courses'
            )
        else:
            collection_jobs[job_id]['status'] = 'completed'
            collection_jobs[job_id]['logs'].append('No courses collected')
        
    except Exception as e:
        collection_jobs[job_id]['status'] = 'failed'
        collection_jobs[job_id]['error'] = str(e)
        collection_jobs[job_id]['logs'].append(f'❌ Error: {str(e)}')


@app.errorhandler(404)
def not_found(e):
    """404 handler"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'available_endpoints': [
            'GET /api/courses',
            'GET /api/courses/<id>',
            'GET /api/courses/youtube/<youtube_id>',
            'GET /api/categories',
            'GET /api/languages',
            'GET /api/stats',
            'POST /api/search',
            'GET /api/health',
            'GET /api/filters'
        ]
    }), 404


@app.errorhandler(500)
def internal_error(e):
    """500 handler"""
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': str(e)
    }), 500


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 5000))
    
    print('=' * 60)
    print('🚀 CourseSpider API Server')
    print('=' * 60)
    print(f'📡 Server running on: http://localhost:{PORT}')
    print('')
    print('Available endpoints:')
    print(f'  GET  /api/courses - Search and filter courses')
    print(f'  GET  /api/courses/<id> - Get specific course')
    print(f'  DELETE /api/courses/<id> - Delete course')
    print(f'  GET  /api/courses/youtube/<id> - Get course by YouTube ID')
    print(f'  GET  /api/categories - List all categories')
    print(f'  GET  /api/languages - List all languages')
    print(f'  GET  /api/stats - Database statistics')
    print(f'  POST /api/search - Advanced search')
    print(f'  POST /api/collect - Start collection job')
    print(f'  GET  /api/collect/status/<job_id> - Get collection status')
    print(f'  GET  /api/health - Health check')
    print(f'  GET  /api/filters - Available filters')
    print('=' * 60)
    
    app.run(host='0.0.0.0', port=PORT, debug=False)
