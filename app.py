from flask import Flask, render_template, request, redirect, session
import psycopg2
import os

app = Flask(__name__)
# IMPORTANT: Change this secret key in a real application!
app.secret_key = 'a-very-secret-key-that-you-should-change'

# --- Database Connection ---
def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database='news_db',
        user='postgres',
        password='$Post++' # Use environment variables for credentials in production
    )
    return conn

# -------------------- USER-FACING ROUTES --------------------
@app.route('/')
def index():
    """Renders the main homepage for all users."""
    conn = get_db_connection()
    cur = conn.cursor()
    # Assuming your user-facing pages show news from all categories
    cur.execute('SELECT title, "publishedAt", "link" FROM "news_2025" ORDER BY "publishedAt" DESC')
    all_news = cur.fetchall()
    conn.close()
    return render_template('index3.html', news=all_news)

# Your other user-facing routes
@app.route('/about')
def about(): return render_template('about.html')
@app.route('/national')
def national(): return render_template("national.html")
@app.route('/international')
def international(): return render_template("international.html")
@app.route('/environment')
def environment(): return render_template("environment.html")
@app.route('/technology')
def technology(): return render_template("technology.html")
@app.route('/contact')
def contact(): return render_template("contact.html")


# -------------------- ADMIN ROUTES --------------------

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Handles admin login."""
    if request.method == 'POST':
        # In a real app, use hashed passwords, not plaintext!
        if request.form['username'] == 'admin' and request.form['password'] == 'admin123':
            session['admin_logged_in'] = True
            return redirect('/admin/dashboard')
        else:
            return render_template('admin_login.html', error='Invalid credentials')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    """Logs the admin out."""
    session.pop('admin_logged_in', None)
    return redirect('/admin/login')

@app.route('/admin/dashboard')
def admin_dashboard():
    """Shows the main admin dashboard with management boxes."""
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')
    return render_template('admin_dashboard.html')

@app.route('/admin/manage/<category>')
def admin_manage_category(category):
    """A dynamic route to manage news for any given category."""
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    icons = {
        "home": "fa-home", "national": "fa-flag", "international": "fa-globe",
        "technology": "fa-microchip", "environmental": "fa-leaf", "live": "fa-broadcast-tower",
        "about": "fa-info-circle", "contact": "fa-envelope"
    }
    icon_class = icons.get(category, "fa-newspaper")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM "news_2025" WHERE category = %s ORDER BY "publishedAt" DESC', (category,))
    news_items = cur.fetchall()
    conn.close()

    return render_template('manage_category.html', 
                           news=news_items, 
                           category_name=category, 
                           icon_class=icon_class)

@app.route('/admin/add', methods=['GET', 'POST'])
def admin_add_news():
    """Handles adding a new news article."""
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    category = request.args.get('category', 'home')

    if request.method == 'POST':
        title = request.form['title']
        publishedAt = request.form.get('date', '2025-01-01')
        link = request.form['link']
        description = request.form['description']
        category_from_form = request.form['category']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO "news_2025" (title, "publishedAt", link, description, category) VALUES (%s, %s, %s, %s, %s)',
            (title, publishedAt, link, description, category_from_form)
        )
        conn.commit()
        conn.close()
        return redirect(f'/admin/manage/{category_from_form}')

    return render_template('admin_add.html', category=category)

@app.route('/admin/edit/<int:news_id>', methods=['GET', 'POST'])
def admin_edit_news(news_id):
    """Handles editing an existing news article."""
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')
    
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        title = request.form['title']
        link = request.form['link']
        description = request.form['description']
        category = request.form['category']
        
        cur.execute(
            'UPDATE "news_2025" SET title=%s, link=%s, description=%s, category=%s WHERE id=%s',
            (title, link, description, category, news_id)
        )
        conn.commit()
        conn.close()
        return redirect(f'/admin/manage/{category}')

    cur.execute('SELECT * FROM "news_2025" WHERE id = %s', (news_id,))
    news_item = cur.fetchone()
    conn.close()
    return render_template('admin_edit.html', news=news_item)

@app.route('/admin/delete/<int:news_id>')
def admin_delete_news(news_id):
    """Handles deleting a news article."""
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    category = request.args.get('category', 'home')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM "news_2025" WHERE id = %s', (news_id,))
    conn.commit()
    conn.close()
    
    return redirect(f'/admin/manage/{category}')

if __name__ == '__main__':
    app.run(debug=True)
