from flask import Flask, render_template, request
import sqlite3
import math

app = Flask(__name__)

def get_players(page, per_page):
    offset = (page - 1) * per_page
    conn = sqlite3.connect('database/players.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM players")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT name, rank, score FROM players ORDER BY score DESC LIMIT ? OFFSET ?", (per_page, offset))
    players = cursor.fetchall()
    conn.close()
    return players, total

@app.route('/')
def index():
    page = int(request.args.get('page', 1))
    per_page = 50
    players, total = get_players(page, per_page)
    total_pages = math.ceil(total / per_page)
    return render_template('index.html', players=players, page=page, total_pages=total_pages)

if __name__ == '__main__':
    app.run(debug=True)
