from flask import Flask, render_template, request, redirect, session
import psycopg2

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

def get_db_connection():
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database='news_db',
        user='postgres',
        password='root'
    )
    return conn

# -------------------- USER SIDE ROUTES --------------------
@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 6
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('SELECT COUNT(*) FROM "news_2025"')
    total_news = cur.fetchone()[0]
    total_pages = min(10, (total_news + per_page - 1) // per_page)

    cur.execute('SELECT title, "publishedAt", "link" FROM "news_2025" ORDER BY "publishedAt" DESC LIMIT %s OFFSET %s', (per_page, offset))
    paginated_news = cur.fetchall()

    cur.execute('SELECT title, "publishedAt", "link" FROM "news_2025" ORDER BY "publishedAt" DESC')
    all_news = cur.fetchall()

    conn.close()

    return render_template('index3.html', news=all_news, paginated_news=paginated_news, page=page, has_prev=page > 1, has_next=page < total_pages, is_last_page=page == total_pages)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/national')
def national():
    return render_template("national.html")

@app.route('/international')
def international():
    return render_template("international.html")

@app.route('/environment')
def environment():
    return render_template("environment.html")

@app.route('/technology')
def technology():
    return render_template("technology.html")

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        print(f"Received message from {name} ({email}): {message}")
    return render_template("contact.html")

@app.route('/news/<path:link>')
def news_detail(link):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM "news_2025" WHERE "link" = %s', (link,))
    news_item = cur.fetchone()
    conn.close()

    if news_item:
        return render_template('news_detail.html', news=news_item)
    else:
        return "News item not found", 404

# -------------------- ADMIN PANEL ROUTES --------------------
@app.route('/admin/signup', methods=['GET', 'POST'])
def admin_signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        return redirect('/admin/login')
    return render_template('admin_signup.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin123':
            session['admin_logged_in'] = True
            return redirect('/admin/dashboard')
        else:
            return render_template('admin_login.html', error='Invalid credentials')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect('/')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM "news_2025" ORDER BY "publishedAt" DESC')
    news_items = cur.fetchall()
    conn.close()

    return render_template('admin_dashboard.html', news=news_items)

@app.route('/admin/add', methods=['GET', 'POST'])
def admin_add_news():
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    if request.method == 'POST':
        title = request.form['title']
        publishedAt = request.form['date']
        link = request.form['link']
        description = request.form['description']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO "news_2025" (title, "publishedAt", link, description) VALUES (%s, %s, %s, %s)', (title, publishedAt, link, description))
        conn.commit()
        conn.close()
        return redirect('/admin/dashboard')

    return render_template('admin_add_news.html')

@app.route('/admin/edit/<int:news_id>', methods=['GET', 'POST'])
def admin_edit_news(news_id):
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        title = request.form['title']
        link = request.form['link']
        description = request.form['description']

        cur.execute('UPDATE "news_2025" SET title=%s, link=%s, description=%s WHERE id=%s', (title, link, description, news_id))
        conn.commit()
        conn.close()
        return redirect('/admin/dashboard')

    cur.execute('SELECT * FROM "news_2025" WHERE id = %s', (news_id,))
    news_item = cur.fetchone()
    conn.close()

    return render_template('admin_edit_news.html', news=news_item)

@app.route('/admin/delete/<int:news_id>')
def admin_delete_news(news_id):
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM "news_2025" WHERE id = %s', (news_id,))
    conn.commit()
    conn.close()
    return redirect('/admin/dashboard')

if __name__ == '__main__':
    app.run(debug=True)
