# 📚 Standalone Course Viewer

This is a pure JavaScript web application that displays YouTube courses **reading directly from SQLite database**. No backend server needed!

## ✨ Features

- **Direct Database Access**: Reads SQLite database file using SQL.js (no export needed!)
- **No Server Required**: Pure HTML + JavaScript - works offline
- **Always Up-to-Date**: Just copy fresh database file monthly
- **Embedded Video Player**: Watch courses directly on your site
- **Search & Filter**: Find courses by category, language, or keyword
- **Responsive Design**: Works on desktop, tablet, and mobile

## 🚀 Quick Start

### 1. Copy Files to Your Website

You only need 2 files:

```
your-website/
├── index.html          (the web app - 25 KB)
└── courses.db          (SQLite database - copies from data/courses.db)
```

**To deploy**:
```bash
# Copy from your CourseSpider project
cp standalone/index.html /path/to/your/website/
cp data/courses.db /path/to/your/website/
```

That's it! Open `index.html` in a browser.

### 2. How It Works

The app uses **SQL.js** (JavaScript SQLite library) to read the database directly in the browser:
- Loads `courses.db` using Fetch API
- Queries courses and lessons using SQL
- No server-side processing needed
- All data processing happens in browser

## 📦 File Sizes

- `index.html`: ~25 KB (the web app)
- `courses.db`: Varies (11 MB for 466 courses, grows with more data)

## 🔄 Updating Courses

When you collect new courses:

1. Collect courses using admin panel (runs collector)
2. Database auto-updates at `data/courses.db`
3. Copy fresh database to your website:
   ```bash
   cp data/courses.db /path/to/your/website/courses.db
   ```

**That's it!** No export, no JavaScript regeneration. Just copy the database file.

## 🎯 Advantages Over JavaScript Export

**Old Method (courses-data.js)**:
- ❌ Need to run `export_to_js.py` after every update
- ❌ Large JavaScript file (43 MB for 466 courses)
- ❌ Browser loads entire dataset into memory
- ❌ Extra step in workflow

**New Method (courses.db)**:
- ✅ Direct database access - no export needed
- ✅ Smaller file size (SQLite is compressed)
- ✅ Lazy loading - only loads what's displayed
- ✅ Just copy database and you're done

## 🎨 Customization

### Change Colors

Edit the CSS in `index.html` to match your brand:

```css
/* Main gradient */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Buttons and accents */
background: #667eea;
```

### Adjust Layout

Change the grid columns in `index.html`:

```css
.courses-grid {
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    /* Change 350px to adjust card width */
}
```

### Change Items Per Page

Edit in `index.html` JavaScript:

```javascript
let coursesPerPage = 12;  // Change to show more/less courses per page
```

## 🌐 Browser Compatibility

Works in all modern browsers:
- ✅ Chrome/Edge (latest)
- ✅ Firefox (latest)
- ✅ Safari 11+ (needs WASM support)
- ✅ Mobile browsers (iOS Safari 11+, Chrome Mobile)

**Note**: Requires WebAssembly support (SQL.js uses WASM)

## 📱 Responsive Breakpoints

- **Desktop**: 1400px max width, 3-4 columns
- **Tablet**: 768px - 1024px, 2 columns
- **Mobile**: < 768px, 1 column

## 🔧 Technical Details

- **Pure JavaScript**: No frameworks or libraries (except SQL.js for database)
- **SQL.js**: WebAssembly SQLite implementation (loaded from CDN)
- **Data Storage**: Binary SQLite database file
- **Database Access**: Client-side SQL queries in browser
- **Search**: Client-side filtering (instant results)
- **Performance**: Handles 500+ courses smoothly, loads on-demand

## 💡 Use Cases

1. **Course Directory**: Add to your learning platform
2. **Resource Page**: Share curated courses on your blog
3. **Monthly Updates**: Just replace database file - no rebuild needed
4. **Offline Access**: Download and use without internet (after initial load)
5. **Embeddable Widget**: Include in WordPress, Wix, or any CMS

## 🚫 Limitations

- Data is static (requires re-export to update)
- Large datasets (1000+ courses) may slow down initial load
- No backend features (comments, ratings, user accounts)
- Videos require internet connection (YouTube embed)

## 🎯 Best Practices

1. **Regular Updates**: Export monthly to keep courses fresh
2. **Image Optimization**: YouTube thumbnails load automatically
3. **SEO**: Add meta tags to `index.html` for better search rankings
4. **CDN**: Host `courses-data.js` on a CDN for faster global access
5. **Compression**: Enable gzip on your web server to reduce file size

## 📊 Performance Tips

- Use browser caching for `courses-data.js`
- Consider pagination for 500+ courses
- Lazy load thumbnails for better initial load time
## 🆘 Troubleshooting

**Problem**: "Database file not found"  
**Solution**: Make sure `courses.db` is in the same folder as `index.html`

**Problem**: "Failed to fetch database"  
**Solution**: Must serve via HTTP/HTTPS (not file://). Use Python: `python -m http.server 8000`

**Problem**: Videos not playing  
**Solution**: Some videos disable embedding - click "🎬 YouTube" button to watch on YouTube

**Problem**: Slow loading  
**Solution**: Database is loaded once on page load. For 1000+ courses, initial load may take 5-10 seconds

## 🚀 Production Deployment

For best performance on your website:

1. **Enable Gzip**: Compress `courses.db` on your web server
   ```nginx
   # Nginx example
   gzip on;
   gzip_types application/octet-stream;
   ```

2. **Browser Caching**: Cache database file for 1 month
   ```nginx
   location ~* \.db$ {
       expires 30d;
   }
   ```

3. **CDN**: Host `courses.db` on CDN for faster global access

4. **HTTPS Required**: Modern browsers require HTTPS for WASM
**Problem**: Search not working  
**Solution**: Ensure browser JavaScript is enabled

## 📄 License

This standalone app is part of the CourseSpider project. Free to use and modify for your needs.
