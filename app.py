
# app.py
from flask import Flask, render_template
import psycopg2

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
        host='localhost',
        database='news_db',
        user='postgres',
        password='$Post++'
    )
    return conn

def get_news():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT title, "publishedAt", "link" FROM "news_2025" ORDER BY "publishedAt" DESC')
    news = cur.fetchall()
    conn.close()
    return news

@app.route('/')
def index():
    news = get_news()
    return render_template('index3.html', news=news)

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

if __name__ == '__main__':
    app.run(debug=True)
