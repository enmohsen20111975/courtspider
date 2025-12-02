// Global variables
let allCourses = [];
let filteredCourses = [];
let currentPage = 1;
let coursesPerPage = 12;
let currentCourse = null;
let currentLesson = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadData();
});

// Load data from SQLite database
async function loadData() {
    try {
        // Show loading message
        document.getElementById('coursesContainer').innerHTML = `
            <div class="loading">
                <h3>Loading courses from database...</h3>
                <p>Please wait while we read courses.db</p>
            </div>
        `;

        // Initialize SQL.js
        const SQL = await initSqlJs({
            locateFile: file => `https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.8.0/${file}`
        });

        // Load database file
        const response = await fetch('courses.db');
        if (!response.ok) {
            throw new Error('Database file not found. Please copy courses.db to this folder.');
        }

        const buffer = await response.arrayBuffer();
        const db = new SQL.Database(new Uint8Array(buffer));

        // Query all courses
        const coursesResult = db.exec(`
            SELECT * FROM courses 
            ORDER BY created_at DESC
        `);

        if (!coursesResult.length) {
            throw new Error('No courses found in database');
        }

        // Parse courses
        const coursesColumns = coursesResult[0].columns;
        const coursesValues = coursesResult[0].values;
        
        allCourses = coursesValues.map(row => {
            const course = {};
            coursesColumns.forEach((col, idx) => {
                course[col] = row[idx];
            });

            // Get lessons for this course
            const lessonsResult = db.exec(`
                SELECT * FROM lessons 
                WHERE course_id = ${course.id}
                ORDER BY idx
            `);

            // Parse lessons
            if (lessonsResult.length > 0) {
                const lessonsColumns = lessonsResult[0].columns;
                const lessonsValues = lessonsResult[0].values;
                
                course.lessons = lessonsValues.map(lessonRow => {
                    const lesson = {};
                    lessonsColumns.forEach((col, idx) => {
                        lesson[col] = lessonRow[idx];
                    });
                    return lesson;
                });
            } else {
                course.lessons = [];
            }

            return course;
        });

        // Set filtered courses to all courses initially
        filteredCourses = allCourses;

        // Calculate stats
        const stats = {
            total_courses: allCourses.length,
            total_lessons: allCourses.reduce((sum, c) => sum + (c.lesson_count || 0), 0),
            total_hours: Math.round(allCourses.reduce((sum, c) => sum + (c.duration_min || 0), 0) / 60),
            categories: [...new Set(allCourses.map(c => c.category))],
            languages: [...new Set(allCourses.map(c => c.language_name))]
        };

        // Update stats display
        document.getElementById('totalCourses').textContent = stats.total_courses.toLocaleString();
        document.getElementById('totalLessons').textContent = stats.total_lessons.toLocaleString();
        document.getElementById('totalHours').textContent = stats.total_hours.toLocaleString();
        document.getElementById('totalCategories').textContent = stats.categories.length;

        // Store stats globally for filters
        window.COURSES_STATS = stats;

        // Populate filters
        populateFilters();

        // Display courses
        displayCourses();

        // Close database
        db.close();

    } catch (error) {
        console.error('Error loading database:', error);
        document.getElementById('coursesContainer').innerHTML = 
            '<div class="no-results">' +
                '<h3>Database Loading Error</h3>' +
                '<p><strong>' + error.message + '</strong></p>' +
                '<p style="margin-top: 15px; color: #718096;">' +
                    'Make sure <strong>courses.db</strong> is in the same folder as this HTML file.' +
                '</p>' +
                '<button onclick="window.location.reload()" style="margin-top: 20px;">' +
                    'Reload Page' +
                '</button>' +
            '</div>';
    }
}

// Populate filter dropdowns
function populateFilters() {
    const categoryFilter = document.getElementById('categoryFilter');
    const languageFilter = document.getElementById('languageFilter');

    // Clear existing options (keep "All" option)
    categoryFilter.innerHTML = '<option value="">All Categories</option>';
    languageFilter.innerHTML = '<option value="">All Languages</option>';

    // Categories
    if (window.COURSES_STATS && window.COURSES_STATS.categories) {
        window.COURSES_STATS.categories.sort().forEach(cat => {
            const option = document.createElement('option');
            option.value = cat;
            option.textContent = cat;
            categoryFilter.appendChild(option);
        });
    }

    // Languages
    if (window.COURSES_STATS && window.COURSES_STATS.languages) {
        window.COURSES_STATS.languages.sort().forEach(lang => {
            const option = document.createElement('option');
            option.value = lang;
            option.textContent = lang;
            languageFilter.appendChild(option);
        });
    }
}

// Apply filters
function applyFilters() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const category = document.getElementById('categoryFilter').value;
    const language = document.getElementById('languageFilter').value;

    filteredCourses = allCourses.filter(course => {
        const matchesSearch = !searchTerm || 
            course.title.toLowerCase().includes(searchTerm) ||
            course.description.toLowerCase().includes(searchTerm) ||
            course.author_name.toLowerCase().includes(searchTerm);
        
        const matchesCategory = !category || course.category === category;
        const matchesLanguage = !language || course.language_name === language;

        return matchesSearch && matchesCategory && matchesLanguage;
    });

    currentPage = 1;
    displayCourses();
}

// Display courses
function displayCourses() {
    const container = document.getElementById('coursesContainer');
    const start = (currentPage - 1) * coursesPerPage;
    const end = start + coursesPerPage;
    const coursesToShow = filteredCourses.slice(start, end);

    if (coursesToShow.length === 0) {
        container.innerHTML = `
            <div class="no-results">
                <h3>No courses found</h3>
                <p>Try adjusting your search or filters.</p>
            </div>
        `;
        document.getElementById('pagination').style.display = 'none';
        return;
    }

    const grid = document.createElement('div');
    grid.className = 'courses-grid';

    coursesToShow.forEach(course => {
        const card = document.createElement('div');
        card.className = 'course-card';
        card.onclick = () => openCourse(course);

        card.innerHTML = `
            <img src="${course.thumbnail || 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIwIiBoZWlnaHQ9IjE4MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMzIwIiBoZWlnaHQ9IjE4MCIgZmlsbD0iIzY2N2VlYSIvPjwvc3ZnPg=='}" 
                 alt="${course.title}" 
                 class="course-thumbnail">
            <div class="course-content">
                <h3 class="course-title">${course.title}</h3>
                <p class="course-author">by ${course.author_name}</p>
                <div class="course-tags">
                    <span class="tag tag-category">${course.category}</span>
                    <span class="tag tag-language">${course.language_name}</span>
                </div>
                <div class="course-meta">
                    <span>${course.lesson_count} lessons</span>
                    <span>${Math.round(course.duration_min / 60)}h</span>
                </div>
            </div>
        `;

        grid.appendChild(card);
    });

    container.innerHTML = '';
    container.appendChild(grid);

    updatePagination();
}

// Update pagination
function updatePagination() {
    const totalPages = Math.ceil(filteredCourses.length / coursesPerPage);
    
    document.getElementById('pageInfo').textContent = `Page ${currentPage} of ${totalPages}`;
    document.getElementById('btnPrev').disabled = currentPage === 1;
    document.getElementById('btnNext').disabled = currentPage === totalPages;
    document.getElementById('pagination').style.display = totalPages > 1 ? 'flex' : 'none';
}

// Pagination controls
function previousPage() {
    if (currentPage > 1) {
        currentPage--;
        displayCourses();
        window.scrollTo(0, 0);
    }
}

function nextPage() {
    const totalPages = Math.ceil(filteredCourses.length / coursesPerPage);
    if (currentPage < totalPages) {
        currentPage++;
        displayCourses();
        window.scrollTo(0, 0);
    }
}

// Open course modal
function openCourse(course) {
    currentCourse = course;
    
    document.getElementById('modalTitle').textContent = course.title;
    document.getElementById('modalAuthor').textContent = 'by ' + course.author_name + ' - ' + course.lesson_count + ' lessons - ' + Math.round(course.duration_min / 60) + ' hours';

    // Show info message if on localhost
    const videoInfo = document.getElementById('videoInfo');
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        videoInfo.style.display = 'block';
    } else {
        videoInfo.style.display = 'none';
    }

    // Load first lesson
    if (course.lessons && course.lessons.length > 0) {
        loadLesson(course.lessons[0]);
        displayLessonsList(course.lessons);
    }

    document.getElementById('courseModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

// Display lessons list
function displayLessonsList(lessons) {
    const container = document.getElementById('lessonsList');
    container.innerHTML = '';

    lessons.forEach((lesson, index) => {
        const item = document.createElement('div');
        item.className = 'lesson-item' + (index === 0 ? ' active' : '');
        item.onclick = () => {
            document.querySelectorAll('.lesson-item').forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            loadLesson(lesson);
        };

        item.innerHTML = `
            <span class="lesson-title">${index + 1}. ${lesson.title}</span>
            <span class="lesson-duration">${formatDuration(lesson.duration_min)}</span>
            <button class="open-youtube-btn" onclick="event.stopPropagation(); openLessonOnYouTube('${lesson.video_id}')">
                🎬 YouTube
            </button>
        `;

        container.appendChild(item);
    });
}

// Load lesson video
function loadLesson(lesson) {
    currentLesson = lesson;
    const videoPlayer = document.getElementById('videoPlayer');
    const videoError = document.getElementById('videoError');
    
    // Hide error message initially
    videoError.style.display = 'none';
    
    // Clear previous video
    videoPlayer.src = '';
    
    // Load new video with all necessary parameters for embedding
    // Using youtube.com instead of youtube-nocookie for better compatibility
    const embedUrl = `https://www.youtube.com/embed/${lesson.video_id}?` + 
        'autoplay=0&' +           // Don't autoplay
        'rel=0&' +                // Don't show related videos
        'modestbranding=1&' +     // Minimal YouTube branding
        'playsinline=1&' +        // Play inline on mobile
        'enablejsapi=1&' +        // Enable JavaScript API
        'origin=' + window.location.origin; // Required for security
    
    videoPlayer.src = embedUrl;
    
    // Note: Some videos may still not work due to YouTube channel settings
    // The error div provides a fallback to open on YouTube directly
}

// Open current video on YouTube
function openCurrentVideoOnYouTube() {
    if (currentLesson) {
        window.open(`https://www.youtube.com/watch?v=${currentLesson.video_id}`, '_blank');
    }
}

// Open specific lesson on YouTube
function openLessonOnYouTube(videoId) {
    window.open(`https://www.youtube.com/watch?v=${videoId}`, '_blank');
}

// Close modal
function closeModal() {
    document.getElementById('courseModal').style.display = 'none';
    document.getElementById('videoPlayer').src = '';
    document.body.style.overflow = 'auto';
}

// Format duration
function formatDuration(minutes) {
    if (minutes < 60) {
        return `${Math.round(minutes)}m`;
    }
    const hours = Math.floor(minutes / 60);
    const mins = Math.round(minutes % 60);
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('courseModal');
    if (event.target === modal) {
        closeModal();
    }
}
