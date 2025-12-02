# CourseSpider - YouTube Course Collector

CourseSpider is a specialized metadata-extraction agent that discovers, verifies, and stores free YouTube courses in a query-friendly format. It continuously monitors YouTube for high-quality, free educational content and normalizes all metadata for easy searching and filtering.

## Features

- **Automated Course Discovery**: Search and collect free YouTube playlists/courses using the YouTube Data API v3
- **Smart Categorization**: Automatically categorize courses into 16 categories (AI/ML, Web Dev, Data Science, etc.)
- **Quality Verification**: Ensure all collected content is freely accessible with no paywalls
- **JSONL Storage**: Store course data in efficient JSONL format for fast querying
- **Semantic Search**: Optional vector database integration for semantic search capabilities
- **Caption Processing**: Optional transcription and embedding generation for improved search
- **REST API**: Built-in search API with filtering and pagination
- **Scheduling**: Automated daily collection at 02:00 UTC
- **Deduplication**: Smart deduplication to avoid collecting the same courses multiple times

## Quick Start

### Prerequisites

- Python 3.8+
- YouTube Data API v3 key ([Get one here](https://console.developers.google.com/))
- Optional: Pinecone account for vector search
- Optional: OpenAI API key for enhanced transcription

### Installation

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd coursespider
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Set environment variables**:
   ```bash
   export YOUTUBE_API_KEY="your_youtube_api_key_here"
   export PINECONE_API_KEY="your_pinecone_key_here"  # Optional
   export PINECONE_ENVIRONMENT="your_pinecone_env"  # Optional
   ```

3. **Validate configuration**:
   ```bash
   python main.py validate
   ```

### Basic Usage

1. **Collect courses once**:
   ```bash
   python main.py collect --keywords "python tutorial" "machine learning" "web development"
   ```

2. **Start scheduled collection** (runs daily at 02:00 UTC):
   ```bash
   python main.py schedule
   ```

3. **Run single collection cycle**:
   ```bash
   python main.py schedule --once
   ```

4. **Start search API**:
   ```bash
   python main.py api --port 5000
   ```

5. **View statistics**:
   ```bash
   python main.py stats
   ```

### API Usage

Once the API is running, you can search for courses:

```bash
# Get all AI/ML courses with at least 10 lessons
curl "http://localhost:5000/courses?category=AI/ML&min_lessons=10"

# Search for Python courses
curl "http://localhost:5000/courses?text=python&category=Web%20Dev"

# Get course recommendations
curl "http://localhost:5000/courses/PLrAXjErJjLtM2sBslQL1g0nW1dW1dW1dW1d"

# Get category statistics
curl "http://localhost:5000/categories"
```

#### Search API Examples

**JavaScript:**
```javascript
// Search for React courses
const response = await fetch('http://localhost:5000/courses?category=Web%20Dev&subcategory=React&min_lessons=5');
const courses = await response.json();

// Advanced search
const searchResponse = await fetch('http://localhost:5000/search', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: "machine learning with python",
    filters: {
      category: "AI/ML",
      min_lessons: 10,
      max_duration: 600
    },
    limit: 20
  })
});
```

**Python:**
```python
import requests

# Basic search
response = requests.get('http://localhost:5000/courses', params={
    'category': 'AI/ML',
    'text': 'deep learning',
    'limit': 10
})
courses = response.json()

# Advanced search
search_data = {
    'query': 'web development full stack',
    'filters': {
        'category': 'Web Dev',
        'min_lessons': 20,
        'max_duration': 1200
    }
}
response = requests.post('http://localhost:5000/search', json=search_data)
results = response.json()
```

## Course Schema

Each course is stored with the following structure:

```json
{
  "youtube_id": "PLrAXjErJjLtM2sBslQL1g0nW1dW1dW1dW1dW1dW",
  "url": "https://www.youtube.com/playlist?list=PLrAXjErJjLtM2sBslQL1g0nW1dW1dW1dW1dW1dW",
  "category": "AI/ML",
  "subcategory": "Deep Learning",
  "title": "Complete Deep Learning Course with TensorFlow",
  "author": {
    "name": "Tech Channel",
    "channel_id": "UCxxxxxxxxxxxxxx",
    "homepage": "https://www.youtube.com/channel/UCxxxxxxxxxxxxxx"
  },
  "description": "A comprehensive course covering deep learning fundamentals...",
  "duration_min": 720,
  "lesson_count": 30,
  "lessons": [
    {
      "idx": 1,
      "title": "Introduction to Neural Networks",
      "video_id": "dQw4w9WgXcQ",
      "duration_min": 15,
      "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/mqdefault.jpg"
    }
    // ... more lessons
  ],
  "last_updated": "2025-01-15T10:30:00Z",
  "license": "Standard YouTube",
  "verified_free": true,
  "scraped_at": "2025-01-15T12:00:00Z"
}
```

## Advanced Features

### Transcription and Embeddings

Enable caption processing for improved search:

```bash
# Transcribe captions and generate embeddings
python main.py transcribe --input free_courses2025-01.jsonl

# Search using semantic similarity
python main.py transcribe --search "machine learning with python"
```

### Semantic Search with Pinecone

To enable vector-based semantic search:

1. Create a Pinecone account and index
2. Set environment variables:
   ```bash
   export PINECONE_API_KEY="your_key"
   export PINECONE_ENVIRONMENT="your_env"
   ```
3. Run transcription to generate embeddings
4. Search will automatically use semantic similarity

### Custom Categories

Modify categories in `config.py`:

```python
CATEGORIES = [
    "AI/ML", "Web Dev", "Mobile", "Cloud", "Cybersecurity", 
    "Data Science", "DevOps", "Backend", "Frontend", 
    "OS/Systems", "Math", "CS-Fundamentals", "Design", 
    "Business", "Languages", "Other",  # Add your categories
    "Your Custom Category"
]
```

## Configuration

All configuration is managed through the `config.py` file and environment variables:

- `YOUTUBE_API_KEY`: YouTube Data API v3 key (required)
- `YOUTUBE_API_DAILY_QUOTA`: Daily API quota limit (default: 10000)
- `MIN_COURSE_DURATION`: Minimum course duration in minutes (default: 60)
- `MAX_PLAYLISTS_PER_CATEGORY`: Max playlists per category per run (default: 50)
- `PINECONE_API_KEY`: Pinecone API key (optional)
- `PINECONE_ENVIRONMENT`: Pinecone environment (optional)
- `ENABLE_TRANSCRIPTION`: Enable caption transcription (default: false)

## Architecture

```
CourseSpider/
├── coursespider.py      # Core collection engine
├── scheduler.py         # Automated scheduling
├── search_api.py        # REST API endpoint
├── transcription.py     # Caption processing & embeddings
├── config.py           # Configuration management
├── main.py             # CLI interface
├── requirements.txt    # Python dependencies
└── data/               # JSONL storage directory
    ├── free_courses2025-01.jsonl
    ├── free_courses2025-02.jsonl
    └── ...
```

## Monitoring

CourseSpider provides built-in monitoring:

- **Log Files**: `courtspider.log`, `scheduler.log`
- **Statistics**: Real-time API usage and collection stats
- **Daily Reports**: Automated summary reports
- **Error Handling**: Comprehensive error logging and recovery

## Legal Considerations

- **Fair Use**: CourseSpider only stores metadata, not video content
- **YouTube ToS**: Respects YouTube's Terms of Service
- **Rate Limiting**: Implemented to prevent API abuse
- **Content Removal**: Supports takedown requests by removing metadata records

## Troubleshooting

### Common Issues

1. **API Quota Exceeded**:
   ```
   Error: Quota limit reached
   ```
   Solution: Wait until next day or increase quota in Google Console

2. **No Courses Found**:
   ```bash
   python main.py validate  # Check configuration
   ```
   Solution: Verify API key and search keywords

3. **Import Errors**:
   ```bash
   pip install -r requirements.txt
   ```
   Solution: Install all dependencies

4. **Permission Errors**:
   ```bash
   chmod +x main.py
   ```
   Solution: Make scripts executable

### Debug Mode

Enable debug logging for detailed troubleshooting:

```bash
python main.py collect --log-level DEBUG
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Check the troubleshooting section above
- Review log files for detailed error messages
- Validate configuration with `python main.py validate`

---

**CourseSpider** - Making YouTube education discoverable and searchable.