#!/usr/bin/env python3
"""
Enhanced CourseSpider - Comprehensive YouTube Course Collector
Collects detailed course metadata including lessons, descriptions, language, etc.
"""

import os
import json
import re
from datetime import datetime
from typing import List, Dict, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class EnhancedCourseCollector:
    def __init__(self, api_key: str):
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        self.api_key = api_key
        self.data_dir = 'data'
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Comprehensive search keywords by category
        self.search_keywords = {
            'AI/ML': [
                'machine learning course', 'deep learning tutorial', 'artificial intelligence course',
                'neural networks tutorial', 'tensorflow course', 'pytorch tutorial', 'AI course',
                'computer vision course', 'NLP tutorial', 'reinforcement learning'
            ],
            'Web Dev': [
                'web development course', 'javascript tutorial', 'react course', 'vue tutorial',
                'angular course', 'node.js tutorial', 'full stack development', 'web programming',
                'HTML CSS tutorial', 'responsive design course', 'frontend development', 'backend development'
            ],
            'Data Science': [
                'data science course', 'python data analysis', 'pandas tutorial', 'data visualization',
                'statistics course', 'SQL tutorial', 'big data course', 'data engineering',
                'jupyter notebook tutorial', 'numpy course'
            ],
            'Mobile': [
                'android development course', 'iOS development tutorial', 'react native course',
                'flutter tutorial', 'mobile app development', 'swift course', 'kotlin tutorial',
                'app development course'
            ],
            'Cloud': [
                'AWS course', 'Azure tutorial', 'google cloud course', 'cloud computing tutorial',
                'docker course', 'kubernetes tutorial', 'serverless course', 'cloud architecture'
            ],
            'Cybersecurity': [
                'cybersecurity course', 'ethical hacking tutorial', 'network security course',
                'penetration testing tutorial', 'information security course', 'CISSP tutorial',
                'security course'
            ],
            'DevOps': [
                'DevOps course', 'CI/CD tutorial', 'jenkins course', 'terraform tutorial',
                'ansible course', 'infrastructure as code', 'site reliability engineering'
            ],
            'Programming': [
                'python programming course', 'java tutorial', 'C++ course', 'javascript course',
                'go programming tutorial', 'rust course', 'programming fundamentals',
                'coding course', 'software development tutorial'
            ],
            'Database': [
                'database course', 'SQL tutorial', 'MongoDB course', 'PostgreSQL tutorial',
                'database design course', 'MySQL tutorial', 'NoSQL course'
            ],
            'Design': [
                'UI design course', 'UX design tutorial', 'graphic design course', 'figma tutorial',
                'web design course', 'design thinking tutorial', 'Adobe XD course'
            ]
        }
    
    def detect_language(self, snippet: Dict) -> str:
        """Detect language from video snippet"""
        title = snippet.get('title', '')
        description = snippet.get('description', '')
        default_language = snippet.get('defaultLanguage') or snippet.get('defaultAudioLanguage') or 'en'
        
        # Language detection patterns
        language_patterns = {
            'en': r'\b(english|tutorial|course|learn|guide)\b',
            'es': r'\b(español|tutorial|curso|aprende|guía)\b',
            'zh': r'[\u4e00-\u9fa5]|(中文|教程|课程)',
            'hi': r'[\u0900-\u097F]|(हिंदी|ट्यूटोरियल)',
            'ar': r'[\u0600-\u06FF]|(عربي|دروس)',
            'pt': r'\b(português|tutorial|curso|aprenda)\b',
            'fr': r'\b(français|tutoriel|cours|apprendre)\b',
            'de': r'\b(deutsch|tutorial|kurs|lernen)\b',
            'ja': r'[\u3040-\u309F\u30A0-\u30FF]|(日本語|チュートリアル)',
            'ko': r'[\uAC00-\uD7AF]|(한국어|튜토리얼)',
            'ru': r'[\u0400-\u04FF]|(русский|учебник)',
            'it': r'\b(italiano|tutorial|corso|imparare)\b',
            'tr': r'\b(türkçe|eğitim|kurs|öğren)\b',
            'id': r'\b(indonesia|tutorial|kursus|belajar)\b',
            'vi': r'\b(tiếng việt|hướng dẫn|khóa học)\b'
        }
        
        text = (title + ' ' + description).lower()
        
        for code, pattern in language_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return code
        
        return default_language
    
    def get_language_name(self, code: str) -> str:
        """Get language name from code"""
        languages = {
            'en': 'English', 'es': 'Spanish', 'zh': 'Chinese', 'hi': 'Hindi',
            'ar': 'Arabic', 'pt': 'Portuguese', 'fr': 'French', 'de': 'German',
            'ja': 'Japanese', 'ko': 'Korean', 'ru': 'Russian', 'it': 'Italian',
            'tr': 'Turkish', 'id': 'Indonesian', 'vi': 'Vietnamese'
        }
        return languages.get(code, 'English')
    
    def parse_duration(self, duration: str) -> int:
        """Parse ISO 8601 duration to minutes"""
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        if not match:
            return 0
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        return hours * 60 + minutes + (1 if seconds > 0 else 0)
    
    def search_playlists(self, keyword: str, max_results: int = 50, language: str = None) -> List[Dict]:
        """Search for playlists by keyword"""
        try:
            params = {
                'part': 'snippet',
                'q': keyword,
                'type': 'playlist',
                'maxResults': max_results,
                'order': 'relevance'
            }
            
            if language:
                params['relevanceLanguage'] = language
            
            request = self.youtube.search().list(**params)
            response = request.execute()
            return response.get('items', [])
        except HttpError as e:
            print(f"Error searching for '{keyword}': {e}")
            return []
    
    def get_playlist_details(self, playlist_id: str) -> Optional[Dict]:
        """Get detailed playlist information"""
        try:
            request = self.youtube.playlists().list(
                part='snippet,contentDetails',
                id=playlist_id
            )
            response = request.execute()
            items = response.get('items', [])
            return items[0] if items else None
        except HttpError as e:
            print(f"Error getting playlist {playlist_id}: {e}")
            return None
    
    def get_playlist_videos(self, playlist_id: str) -> List[Dict]:
        """Get all videos in a playlist"""
        videos = []
        page_token = None
        
        try:
            while True:
                request = self.youtube.playlistItems().list(
                    part='snippet,contentDetails',
                    playlistId=playlist_id,
                    maxResults=50,
                    pageToken=page_token
                )
                response = request.execute()
                
                videos.extend(response.get('items', []))
                page_token = response.get('nextPageToken')
                
                if not page_token:
                    break
            
            return videos
        except HttpError as e:
            print(f"Error getting videos for playlist {playlist_id}: {e}")
            return []
    
    def get_video_details(self, video_ids: List[str]) -> List[Dict]:
        """Get video details (duration, views, etc.)"""
        if not video_ids:
            return []
        
        try:
            request = self.youtube.videos().list(
                part='snippet,contentDetails,statistics',
                id=','.join(video_ids)
            )
            response = request.execute()
            return response.get('items', [])
        except HttpError as e:
            print(f"Error getting video details: {e}")
            return []
    
    def get_channel_details(self, channel_id: str) -> Optional[Dict]:
        """Get channel details"""
        try:
            request = self.youtube.channels().list(
                part='snippet,statistics',
                id=channel_id
            )
            response = request.execute()
            items = response.get('items', [])
            return items[0] if items else None
        except HttpError as e:
            print(f"Error getting channel {channel_id}: {e}")
            return None
    
    def extract_tags(self, text: str) -> List[str]:
        """Extract tags from text"""
        common_tags = [
            'beginner', 'intermediate', 'advanced', 'tutorial', 'course', 'complete',
            'full', 'crash course', 'bootcamp', 'masterclass', 'certification',
            'project', 'hands-on', 'practical', 'theory', '2024', '2025'
        ]
        
        tags = []
        lower_text = text.lower()
        
        for tag in common_tags:
            if tag in lower_text:
                tags.append(tag)
        
        return tags
    
    def determine_subcategory(self, category: str, text: str) -> str:
        """Determine subcategory based on title and description"""
        text = text.lower()
        
        if category == 'Web Dev':
            if 'react' in text:
                return 'React'
            elif 'vue' in text:
                return 'Vue.js'
            elif 'angular' in text:
                return 'Angular'
            elif 'node' in text:
                return 'Node.js'
            elif 'frontend' in text:
                return 'Frontend'
            elif 'backend' in text:
                return 'Backend'
            elif 'fullstack' in text or 'full stack' in text:
                return 'Full Stack'
        elif category == 'AI/ML':
            if 'tensorflow' in text:
                return 'TensorFlow'
            elif 'pytorch' in text:
                return 'PyTorch'
            elif 'deep learning' in text:
                return 'Deep Learning'
            elif 'computer vision' in text:
                return 'Computer Vision'
            elif 'nlp' in text or 'natural language' in text:
                return 'NLP'
        elif category == 'Programming':
            if 'python' in text:
                return 'Python'
            elif 'javascript' in text:
                return 'JavaScript'
            elif 'java' in text and 'javascript' not in text:
                return 'Java'
            elif 'c++' in text:
                return 'C++'
        
        return category
    
    def process_playlist(self, playlist_item: Dict, category: str) -> Optional[Dict]:
        """Process a playlist into course format"""
        playlist_id = playlist_item.get('id', {}).get('playlistId') or playlist_item.get('id')
        print(f"Processing: {playlist_item['snippet']['title']}")
        
        # Get detailed playlist info
        playlist_details = self.get_playlist_details(playlist_id)
        if not playlist_details:
            return None
        
        # Get all videos in playlist
        playlist_videos = self.get_playlist_videos(playlist_id)
        if len(playlist_videos) < 5:
            print(f"  ⚠️  Skipping: Only {len(playlist_videos)} videos (minimum 5 required)")
            return None
        
        # Get video details in batches of 50
        video_ids = [v['contentDetails']['videoId'] for v in playlist_videos]
        video_details = []
        
        for i in range(0, len(video_ids), 50):
            batch = video_ids[i:i+50]
            details = self.get_video_details(batch)
            video_details.extend(details)
        
        # Get channel details
        channel_id = playlist_details['snippet']['channelId']
        channel_details = self.get_channel_details(channel_id)
        
        # Calculate total duration and build lessons
        total_duration = 0
        lessons = []
        
        for i, video in enumerate(video_details):
            duration = self.parse_duration(video['contentDetails']['duration'])
            total_duration += duration
            
            lessons.append({
                'idx': i + 1,
                'title': video['snippet']['title'],
                'video_id': video['id'],
                'duration_min': duration,
                'description': video['snippet'].get('description', ''),
                'thumbnail': video['snippet']['thumbnails'].get('medium', {}).get('url', ''),
                'published_at': video['snippet']['publishedAt'],
                'view_count': int(video.get('statistics', {}).get('viewCount', 0)),
                'like_count': int(video.get('statistics', {}).get('likeCount', 0))
            })
        
        # Detect language
        language_code = self.detect_language(playlist_details['snippet'])
        language_name = self.get_language_name(language_code)
        
        # Determine subcategory
        text = playlist_details['snippet']['title'] + ' ' + playlist_details['snippet']['description']
        subcategory = self.determine_subcategory(category, text)
        
        # Build course object
        course = {
            'youtube_id': playlist_id,
            'url': f"https://www.youtube.com/playlist?list={playlist_id}",
            'category': category,
            'subcategory': subcategory,
            'title': playlist_details['snippet']['title'],
            'author': {
                'name': playlist_details['snippet']['channelTitle'],
                'channel_id': channel_id,
                'homepage': f"https://www.youtube.com/channel/{channel_id}",
                'subscribers': int(channel_details.get('statistics', {}).get('subscriberCount', 0)) if channel_details else 0
            },
            'description': playlist_details['snippet'].get('description', ''),
            'duration_min': total_duration,
            'lesson_count': len(lessons),
            'lessons': lessons,
            'language': language_code,
            'language_name': language_name,
            'thumbnail': playlist_details['snippet']['thumbnails'].get('high', {}).get('url', ''),
            'published_at': playlist_details['snippet']['publishedAt'],
            'last_updated': datetime.utcnow().isoformat() + 'Z',
            'verified_free': True,
            'scraped_at': datetime.utcnow().isoformat() + 'Z',
            'tags': self.extract_tags(text)
        }
        
        print(f"  ✓ Collected: {len(lessons)} lessons, {total_duration} min, {language_name}")
        return course
    
    def save_courses(self, courses: List[Dict], filename: str):
        """Save courses to JSONL file"""
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            for course in courses:
                f.write(json.dumps(course, ensure_ascii=False) + '\n')
        print(f"\n✓ Saved {len(courses)} courses to {filename}")
    
    def collect_all(self, max_per_category: int = 10) -> List[Dict]:
        """Collect courses for all categories"""
        print('=' * 60)
        print('Enhanced CourseSpider - Starting Collection')
        print('=' * 60)
        print(f"Categories: {len(self.search_keywords)}")
        print(f"Max courses per category: {max_per_category}")
        print('=' * 60)
        print()
        
        all_courses = []
        timestamp = datetime.now().strftime('%Y-%m-%d')
        
        for category, keywords in self.search_keywords.items():
            print(f"\n📚 Category: {category}")
            print('-' * 60)
            
            category_courses = []
            
            for keyword in keywords:
                if len(category_courses) >= max_per_category:
                    break
                
                print(f"\n🔍 Searching: \"{keyword}\"")
                playlists = self.search_playlists(keyword, 10)
                
                for playlist in playlists:
                    if len(category_courses) >= max_per_category:
                        break
                    
                    try:
                        course = self.process_playlist(playlist, category)
                        if course:
                            category_courses.append(course)
                            all_courses.append(course)
                    except Exception as e:
                        print(f"  ✗ Error processing playlist: {e}")
            
            print(f"\n✓ Collected {len(category_courses)} courses for {category}")
        
        # Save to file
        filename = f"courses_{timestamp}.jsonl"
        self.save_courses(all_courses, filename)
        
        # Print summary
        print('\n' + '=' * 60)
        print('Collection Complete!')
        print('=' * 60)
        print(f"Total courses: {len(all_courses)}")
        print(f"File: {filename}")
        
        language_counts = {}
        for course in all_courses:
            lang = course['language_name']
            language_counts[lang] = language_counts.get(lang, 0) + 1
        
        print(f"Languages: {len(language_counts)}")
        for lang, count in language_counts.items():
            print(f"  - {lang}: {count}")
        print('=' * 60)
        
        return all_courses


if __name__ == '__main__':
    import sys
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv('YOUTUBE_API_KEY')
    
    if not api_key:
        print('❌ Error: YOUTUBE_API_KEY not found in environment variables')
        print('Please set it in your .env file or export it:')
        print('  export YOUTUBE_API_KEY="your_api_key"')
        sys.exit(1)
    
    max_per_category = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    
    collector = EnhancedCourseCollector(api_key)
    collector.collect_all(max_per_category)
