import sqlite3
import math
from jinja2 import Template

DB_PATH = 'backend/players.db'
PLAYERS_PER_PAGE = 100

# for memes <link href="https://fonts.googleapis.com/css2?family=Comic+Neue:wght@400;700&display=swap" rel="stylesheet">

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Recent Daily Stats</title>
    <link rel="stylesheet" href="css/styles.css">
    <script>
        function searchPage(totalPages, sortBy) {
            const input = document.getElementById('page-input').value;
            let page = parseInt(input, 10);
            if (isNaN(page) || page < 1) {
                page = 1;
            } else if (page > totalPages) {
                page = totalPages;
            }
            if (sortBy === 'score') {
                window.location.href = 'page' + page + '.html';
            } else if (sortBy === 'total_score') {
                window.location.href = 'sorted_by_score_page' + page + '.html';
            }
        }
        document.addEventListener('DOMContentLoaded', function() {
            const input = document.getElementById('page-input');
            input.addEventListener('keydown', function(event) {
                if (event.key === 'Enter') {
                    searchPage({{ total_pages }}, '{{ sort_by }}');
                }
            });
        });
    </script>
</head>
<body>
    <h1>Recent Daily Stats</h1>
    <p class="summary">Summary of Nuclear Throne daily runs starting from July 1st, 2024</p>
    <p class="summary">Updates everyday at 3:00 UTC</p>
    <p class="summary">Page {{ page }} of {{ total_pages }}</p>
    <div class="sort-container">
        <button onclick="window.location.href='{{ 'sorted_by_score.html' if sort_by == 'score' else 'index.html' }}'">
            Sort by {{ 'Total Score' if sort_by == 'score' else 'Rating' }}
        </button>
    </div>
    <div class="top-controls">
        <div class="search-container">
            <input type="text" id="page-input" placeholder="Select page" />
            <button onclick="searchPage({{ total_pages }}, '{{ sort_by }}')">Go</button>
        </div>
        <div class="navigation">
            {% if page > 1 %}
                <a href="{{ 'sorted_by_score_page' if sort_by == 'total_score' else 'page' }}{{ page - 1 }}.html">Previous</a>
            {% endif %}
            {% if page < total_pages %}
                <a href="{{ 'sorted_by_score_page' if sort_by == 'total_score' else 'page' }}{{ page + 1 }}.html">Next</a>
            {% endif %}
        </div>
    </div>
    <table>
        <tr>
            <th>Rank</th>
            <th>Name</th>
            <th>Rating</th>
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
            <a href="{{ 'sorted_by_score_page' if sort_by == 'total_score' else 'page' }}{{ page - 1 }}.html">Previous</a>
        {% endif %}
        {% if page < total_pages %}
            <a href="{{ 'sorted_by_score_page' if sort_by == 'total_score' else 'page' }}{{ page + 1 }}.html">Next</a>
        {% endif %}
    </div>
</body>
</html>'''

def fetch_players(order_by='score'):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = f"""
        SELECT 
            ROW_NUMBER() OVER (ORDER BY {order_by} DESC) as row_index,
            name,
            score,
            killcount
        FROM players
    """
    cursor.execute(query)
    players = [{'rank': row[0], 'name': row[1], 'points': row[2], 'total_score': row[3]} for row in cursor.fetchall()]
    conn.close()
    return players

def generate_html(players, page, total_pages, sort_by):
    template = Template(HTML_TEMPLATE)
    return template.render(players=players, page=page, total_pages=total_pages, sort_by=sort_by)

if __name__ == '__main__':
    players = fetch_players(order_by='score')
    total_players = len(players)
    total_pages = math.ceil(total_players / PLAYERS_PER_PAGE)

    for page in range(1, total_pages + 1):
        start = (page - 1) * PLAYERS_PER_PAGE
        end = start + PLAYERS_PER_PAGE
        page_players = players[start:end]
        html_content = generate_html(page_players, page, total_pages, sort_by='score')
        with open(f'page{page}.html', 'w', encoding='utf-8') as f:
            f.write(html_content)

    players_sorted_by_score = fetch_players(order_by='killcount')
    total_players = len(players_sorted_by_score)
    total_pages = math.ceil(total_players / PLAYERS_PER_PAGE)

    for page in range(1, total_pages + 1):
        start = (page - 1) * PLAYERS_PER_PAGE
        end = start + PLAYERS_PER_PAGE
        page_players = players_sorted_by_score[start:end]
        html_content = generate_html(page_players, page, total_pages, sort_by='total_score')
        with open(f'sorted_by_score_page{page}.html', 'w', encoding='utf-8') as f:
            f.write(html_content)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write('<meta http-equiv="refresh" content="0; URL=page1.html" />')

    with open('sorted_by_score.html', 'w', encoding='utf-8') as f:
        f.write('<meta http-equiv="refresh" content="0; URL=sorted_by_score_page1.html" />')
