import sqlite3
import math
from jinja2 import Template

DB_PATH = 'backend/players.db'
PLAYERS_PER_PAGE = 100

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Recent Daily Stats</title>
    <link rel="stylesheet" href="css/styles.css">
</head>
<body>
    <h1>Recent Daily Stats</h1>
    <p class="summary">Summary of Nuclear Throne daily runs starting from July 1st, 2024</p>
    <p class="summary">Page {{ page }} of {{ total_pages }}</p>
    <div class="navigation">
        {% if page > 1 %}
            <a href="page{{ page - 1 }}.html">Previous</a>
        {% endif %}
        {% if page < total_pages %}
            <a href="page{{ page + 1 }}.html">Next</a>
        {% endif %}
    </div>
    <table>
        <tr>
            <th>Rank</th>
            <th>Name</th>
            <th>Points</th>
            <th>Total Score</th>
        </tr>
        {% for player in players %}
        <tr>
            <td>{{ player.rank }}</td>
            <td>{{ player.name }}</td>
            <td>{{ player.points }}</td>
            <td>{{ player.total_score }}</td>
        </tr>
        {% endfor %}
    </table>
    <p class="summary">Page {{ page }} of {{ total_pages }}</p>
    <div class="navigation">
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
    cursor.execute("""
        SELECT 
            ROW_NUMBER() OVER (ORDER BY score DESC) as row_index,
            name,
            score,
            killcount
        FROM players
    """)
    players = [{'rank': row[0], 'name': row[1], 'points': row[2], 'total_score': row[3]} for row in cursor.fetchall()]
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
