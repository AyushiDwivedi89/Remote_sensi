from flask import Flask, render_template, request, redirect, session
import psycopg2

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# --- Database Connection Function ---
def get_db_connection():
    conn = psycopg2.connect(
        host='localhost',
        port=5433, 
        database='newdb',
        user='postgres',
        password='123456'
    )
    return conn

# --- Home Page Route ---
@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 6
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cur = conn.cursor()

    # Total news count
    cur.execute('SELECT COUNT(*) FROM "News_2025"')
    total_news = cur.fetchone()[0]
    total_pages = min(10, (total_news + per_page - 1) // per_page)

    # Paginated News
    cur.execute(
        'SELECT title, "publishedAt", "link" FROM "News_2025" ORDER BY "publishedAt" DESC LIMIT %s OFFSET %s',
        (per_page, offset)
    )
    paginated_news = cur.fetchall()

    # All News
    cur.execute('SELECT title, "publishedAt", "link" FROM "News_2025" ORDER BY "publishedAt" DESC')
    all_news = cur.fetchall()

    conn.close()

    return render_template(
        'index3.html',
        news=all_news,
        paginated_news=paginated_news,
        page=page,
        has_prev=page > 1,
        has_next=page < total_pages,
        is_last_page=page == total_pages
    )

# --- About Page Route ---
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/national')
def national():
    news = [
        ("PM Launches Green Energy Mission", "2025-07-03", "#"),
        ("Supreme Court Rules on River Rights", "2025-07-02", "#"),
        ("Massive Rainfall Disrupts North India", "2025-07-01", "#"),
        ("Parliament Passes Education Bill", "2025-06-30", "#"),
        ("ISRO Announces Gaganyaan Timeline", "2025-06-29", "#"),
        ("Election Commission Prepares for State Polls", "2025-06-28", "#")
    ]
    return render_template("national.html", news=news)

@app.route('/international')
def international():
    news = [
        ("UN Holds Emergency Climate Session", "2025-07-04", "#"),
        ("Tech Giants Sign Global AI Agreement", "2025-07-03", "#"),
        ("Massive Flooding in Central Europe", "2025-07-02", "#"),
        ("World Bank Issues Economic Outlook", "2025-07-01", "#"),
        ("NASA Discovers Signs of Ice on Mars", "2025-06-30", "#"),
        ("Protests Erupt Across South America", "2025-06-29", "#")
    ]
    return render_template("international.html", news=news)

@app.route('/environment')
def environment():
    news = [
        ("India’s Clean Air Mission Expands to 100 Cities", "2025-07-04", "#"),
        ("Cyclone Shaheen Impacts Coastal Ecosystems", "2025-07-03", "#"),
        ("New Tree Plantation Drive in Rajasthan", "2025-07-02", "#"),
        ("Himalayan Glaciers Retreating Faster, Study Finds", "2025-07-01", "#"),
        ("Maharashtra Sets Record for Solar Power Output", "2025-06-30", "#"),
        ("Plastic Ban Reinforced Across Major Metro Cities", "2025-06-29", "#")
    ]
    return render_template("environment.html", news=news)

@app.route('/technology')
def technology():
    news = [
        ("Apple Unveils AI Features in iOS 19", "2025-07-04", "#"),
        ("India Launches National Quantum Computing Hub", "2025-07-03", "#"),
        ("OpenAI Releases New Multimodal GPT Model", "2025-07-02", "#"),
        ("Google’s Project Astra Aims for Real-Time AI Assistants", "2025-07-01", "#"),
        ("Tesla Expands Robotaxi Trials Across Asia", "2025-06-30", "#"),
        ("SpaceX Internet Constellation Now Global", "2025-06-29", "#")
    ]
    return render_template("technology.html", news=news)

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
    cur.execute('SELECT * FROM "News_2025" WHERE "link" = %s', (link,))
    news_item = cur.fetchone()
    conn.close()

    if news_item:
        return render_template('news_detail.html', news=news_item)
    else:
        return "News item not found", 404

# --- Admin Login ---
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
    return render_template('admin_dashboard.html')

@app.route('/admin/edit/<category>', methods=['GET', 'POST'])
def edit_category(category):
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        title = request.form['title']
        publishedAt = request.form['date']
        link = request.form['link']
        cur.execute('INSERT INTO "News_2025" (title, "publishedAt", link, category) VALUES (%s, %s, %s, %s)',
                    (title, publishedAt, link, category))
        conn.commit()

    cur.execute('SELECT title, "publishedAt", link FROM "News_2025" WHERE category = %s ORDER BY "publishedAt" DESC', (category,))
    news_items = cur.fetchall()
    conn.close()

    return render_template('admin_edit.html', news=news_items, category=category)

# --- Run the App ---
if __name__ == '__main__':
    app.run(debug=True)
