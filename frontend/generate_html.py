import sqlite3
import math
from jinja2 import Template

DB_PATH = 'database/players.db'
PLAYERS_PER_PAGE = 100

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Top Players - Page {{ page }}</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <h1>Top Players - Page {{ page }}</h1>
    <table>
        <tr>
            <th>Name</th>
            <th>Rank</th>
            <th>Score</th>
        </tr>
        {% for player in players %}
        <tr>
            <td>{{ player.name }}</td>
            <td>{{ player.rank }}</td>
            <td>{{ player.score }}</td>
        </tr>
        {% endfor %}
    </table>
    <div>
        {% if page > 1 %}
            <a href="page{{ page - 1 }}.html">Previous</a>
        {% endif %}
        {% if page < total_pages %}
            <a href="page{{ page + 1 }}.html">Next</a>
        {% endif %}
    </div>
</body>
</html>'''

def fetch_players():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, rank, score FROM players ORDER BY score DESC")
    players = [{'name': row[0], 'rank': row[1], 'score': row[2]} for row in cursor.fetchall()]
    conn.close()
    return players

def generate_html(players, page, total_pages):
    template = Template(HTML_TEMPLATE)
    return template.render(players=players, page=page, total_pages=total_pages)

if __name__ == '__main__':
    players = fetch_players()
    total_players = len(players)
    total_pages = math.ceil(total_players / PLAYERS_PER_PAGE)

    for page in range(1, total_pages + 1):
        start = (page - 1) * PLAYERS_PER_PAGE
        end = start + PLAYERS_PER_PAGE
        page_players = players[start:end]
        html_content = generate_html(page_players, page, total_pages)
        with open(f'page{page}.html', 'w', encoding='utf-8') as f:
            f.write(html_content)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write('<meta http-equiv="refresh" content="0; URL=page1.html" />')
