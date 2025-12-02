# WordPress Deployment Instructions

## Method 1: Upload to WordPress Directory

### Step 1: Upload Files
Upload these 4 files to your WordPress hosting:
```
/wp-content/uploads/free-courses/
├── index.html
├── styles.css
├── app.js
└── courses.db
```

### Step 2: Access Your App
Visit: `https://yoursite.com/wp-content/uploads/free-courses/index.html`

### Step 3: Embed in WordPress Page (Optional)
Edit any WordPress page and add this HTML block:

```html
<iframe 
    src="/wp-content/uploads/free-courses/index.html" 
    width="100%" 
    height="900px" 
    frameborder="0"
    style="border: none; max-width: 100%;">
</iframe>
```

---

## Method 2: Full Page Template

### Step 1: Create Custom Page Template

Create file: `/wp-content/themes/YOUR-THEME/template-courses.php`

```php
<?php
/**
 * Template Name: Free Courses
 */
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Free Programming Courses - <?php bloginfo('name'); ?></title>
    <link rel="stylesheet" href="<?php echo get_template_directory_uri(); ?>/courses/styles.css">
</head>
<body>
    <!-- Your courses app HTML here -->
    <?php include(get_template_directory() . '/courses/content.html'); ?>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.8.0/sql-wasm.js"></script>
    <script src="<?php echo get_template_directory_uri(); ?>/courses/app.js"></script>
</body>
</html>
```

### Step 2: Upload App Files
Put in: `/wp-content/themes/YOUR-THEME/courses/`
- styles.css
- app.js
- courses.db
- content.html (the body content from index.html)

### Step 3: Create WordPress Page
1. In WordPress admin → Pages → Add New
2. Title: "Free Courses"
3. Template: Select "Free Courses" from page attributes
4. Publish

---

## Method 3: Simple Plugin (Recommended)

### Create file: `/wp-content/plugins/free-courses/free-courses.php`

```php
<?php
/**
 * Plugin Name: Free Programming Courses
 * Description: Display curated YouTube programming courses
 * Version: 1.0
 * Author: Your Name
 */

function free_courses_shortcode() {
    $plugin_url = plugins_url('', __FILE__);
    
    // Enqueue scripts and styles
    wp_enqueue_style('courses-style', $plugin_url . '/styles.css');
    wp_enqueue_script('sql-js', 'https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.8.0/sql-wasm.js', array(), '1.8.0', true);
    wp_enqueue_script('courses-app', $plugin_url . '/app.js', array('sql-js'), '1.0', true);
    
    // Return the HTML
    ob_start();
    include(__DIR__ . '/content.html');
    return ob_get_clean();
}
add_shortcode('free_courses', 'free_courses_shortcode');
```

### Plugin Structure:
```
/wp-content/plugins/free-courses/
├── free-courses.php
├── styles.css
├── app.js
├── courses.db
└── content.html
```

### Usage:
Add to any page/post:
```
[free_courses]
```

---

## Important Notes:

### ✅ Will Work:
- WordPress with HTTP/HTTPS ✓
- Real domain names ✓
- YouTube embeds (on real domain) ✓
- Database loading ✓

### ❌ Won't Work:
- Opening index.html by double-clicking ✗
- File:// protocol ✗
- Localhost (YouTube blocks it) ⚠️

### Database Updates:
To update courses:
1. Generate new `courses.db` using your collector
2. Upload to replace old `courses.db`
3. Done! (No code changes needed)

---

## Testing Before Deployment:

### Test on Local WordPress:
If you have local WordPress (XAMPP, Local by Flywheel, etc.):
1. Put files in `/htdocs/wp-content/uploads/courses/`
2. Access via `http://localhost/wp-content/uploads/courses/index.html`
3. YouTube still won't work (localhost issue)
4. But database and UI will work!

### Test with Python Server (Current):
```bash
cd standalone
python serve.py
# Visit: http://localhost:8080/index.html
```
- Database works ✓
- UI works ✓
- YouTube blocked (normal for localhost) ⚠️

---

## Troubleshooting:

**Problem:** "Failed to fetch courses.db"
**Solution:** Make sure all files are in the same directory and served via HTTP/HTTPS

**Problem:** YouTube videos don't play
**Solution:** 
1. Check if on real domain (not localhost)
2. Use "Open on YouTube" buttons as fallback
3. Some videos are restricted by owner (normal)

**Problem:** Page looks broken
**Solution:** Check CSS file is loading (view source, check paths)

---

## File Sizes (Current):
- index.html: 3 KB
- styles.css: 12 KB
- app.js: 14 KB
- courses.db: 55 MB (grows with more courses)

**Total:** ~55 MB (acceptable for WordPress hosting)

---

## Performance Tips:

1. **Enable Gzip** in WordPress (.htaccess):
```apache
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/css text/javascript application/javascript
</IfModule>
```

2. **Browser Caching** for database:
```apache
<FilesMatch "\.(db)$">
    Header set Cache-Control "max-age=2592000, public"
</FilesMatch>
```

3. **CDN** (optional): Host courses.db on CDN for faster loading

---

## Ready to Deploy? ✨

**Simplest method:** Use Method 1 (Upload to wp-content/uploads)
- Takes 2 minutes
- No coding required
- Works immediately
- Easy to update

**Best for integration:** Use Method 3 (Plugin + Shortcode)
- Professional
- Reusable via shortcode
- Easy to add to multiple pages
- Updates via WordPress admin
