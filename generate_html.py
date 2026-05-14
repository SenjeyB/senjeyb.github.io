import sqlite3
import math
from jinja2 import Template

DB_PATH = 'backend/players.db'
PLAYERS_PER_PAGE = 100

NT_TOURNAMENT_URL = 'https://senjeyb.github.io/nt_tournament_stats/'
NT_ICON_BASE = 'https://senjeyb.github.io/nt_tournament_stats/characters'

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <meta name="theme-color" content="#7cb342">
    <meta name="description" content="Daily Nuclear Throne leaderboard aggregated from Thronebutt since July 2024.">
    <title>NT Daily Stats — {{ 'Rating' if sort_by == 'score' else 'Total Score' }} · Page {{ page }}</title>
    <link rel="icon" type="image/png" href="{{ icon_base }}/yv.png">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="css/styles.css">
    <script>
        const TOTAL_PAGES = {{ total_pages }};
        const SORT_BY = '{{ sort_by }}';
        function jumpToPage() {
            const input = document.getElementById('page-input');
            let page = parseInt(input.value, 10);
            if (isNaN(page) || page < 1) page = 1;
            else if (page > TOTAL_PAGES) page = TOTAL_PAGES;
            const prefix = SORT_BY === 'score' ? 'page' : 'sorted_by_score_page';
            window.location.href = prefix + page + '.html';
        }
        function filterPlayers() {
            const q = (document.getElementById('player-filter').value || '').trim().toLowerCase();
            const rows = document.querySelectorAll('#players-table tbody tr');
            let shown = 0;
            rows.forEach(function (row) {
                const name = (row.dataset.name || '').toLowerCase();
                const match = !q || name.indexOf(q) !== -1;
                row.style.display = match ? '' : 'none';
                if (match) shown++;
            });
            const count = document.getElementById('filter-count');
            count.textContent = q ? (shown + ' match' + (shown === 1 ? '' : 'es') + ' on this page') : '';
        }
        document.addEventListener('DOMContentLoaded', function () {
            const pageInput = document.getElementById('page-input');
            if (pageInput) {
                pageInput.addEventListener('keydown', function (e) { if (e.key === 'Enter') jumpToPage(); });
            }
            const filter = document.getElementById('player-filter');
            if (filter) filter.addEventListener('input', filterPlayers);
            const burger = document.getElementById('burger');
            const nav = document.getElementById('main-nav');
            if (burger && nav) {
                burger.addEventListener('click', function () {
                    const open = nav.classList.toggle('open');
                    burger.setAttribute('aria-expanded', open ? 'true' : 'false');
                });
            }
        });
    </script>
</head>
<body>
    <header class="site-header">
        <a class="brand" href="index.html">
            <img class="brand-icon" src="{{ icon_base }}/yv.png" alt="" width="32" height="32">
            <span class="brand-text">
                <span class="brand-title">NT Daily Stats</span>
                <span class="brand-sub">Nuclear Throne · Thronebutt leaderboard</span>
            </span>
        </a>
        <button id="burger" class="burger" aria-label="Toggle navigation" aria-expanded="false" aria-controls="main-nav">
            <span></span><span></span><span></span>
        </button>
        <nav id="main-nav" class="main-nav" aria-label="Main">
            <a class="nav-link {{ 'active' if sort_by == 'score' else '' }}" href="index.html">Daily Rating</a>
            <a class="nav-link {{ 'active' if sort_by == 'total_score' else '' }}" href="sorted_by_score.html">Total Score</a>
            <a class="nav-link external" href="{{ nt_tournament_url }}" target="_blank" rel="noopener">NT Tournament <span aria-hidden="true">↗</span></a>
            <a class="nav-link external" href="https://github.com/senjeyb/senjeyb.github.io" target="_blank" rel="noopener">GitHub <span aria-hidden="true">↗</span></a>
        </nav>
    </header>

    <main class="container">
        <section class="hero">
            <h1>Daily Run Standings</h1>
            <p class="hero-sub">Aggregated daily run data from <a href="https://thronebutt.com" target="_blank" rel="noopener">thronebutt.com</a>, starting <strong>July 1st, 2024</strong>. Updates automatically every day at <strong>03:00 UTC</strong>.</p>
        </section>

        <section class="stats-grid" aria-label="Summary">
            <div class="stat-card">
                <span class="stat-label">Tracked Players</span>
                <span class="stat-value">{{ '{:,}'.format(total_players) }}</span>
                <span class="stat-detail">since 2024-07-01</span>
            </div>
            <div class="stat-card">
                <span class="stat-label">Top {{ 'Rating' if sort_by == 'score' else 'Total Score' }}</span>
                <span class="stat-value">{{ '{:,}'.format(top_value) }}</span>
                <span class="stat-detail" title="{{ top_name }}">{{ top_name }}</span>
            </div>
            <div class="stat-card">
                <span class="stat-label">Sorted By</span>
                <span class="stat-value">{{ 'Rating' if sort_by == 'score' else 'Total Score' }}</span>
                <a class="stat-link" href="{{ 'sorted_by_score.html' if sort_by == 'score' else 'index.html' }}">
                    Switch to {{ 'Total Score' if sort_by == 'score' else 'Rating' }} ↔
                </a>
            </div>
            <div class="stat-card">
                <span class="stat-label">Page</span>
                <span class="stat-value">{{ page }} / {{ total_pages }}</span>
                <span class="stat-detail">{{ players_per_page }} per page</span>
            </div>
        </section>

        <section class="controls" aria-label="Page controls">
            <div class="filter">
                <input id="player-filter" type="search" placeholder="🔎 Filter players on this page…" autocomplete="off" aria-label="Filter players on this page" />
                <span id="filter-count" class="filter-count" role="status" aria-live="polite"></span>
            </div>
            <div class="page-jump">
                <label class="visually-hidden" for="page-input">Jump to page</label>
                <input id="page-input" type="number" min="1" max="{{ total_pages }}" placeholder="Page #" />
                <button type="button" onclick="jumpToPage()">Go</button>
            </div>
        </section>

        <div class="table-wrap">
            <table id="players-table">
                <thead>
                    <tr>
                        <th class="col-rank" scope="col">Rank</th>
                        <th class="col-name" scope="col">Name</th>
                        <th class="col-rating {{ 'sorted' if sort_by == 'score' else '' }}" scope="col">Rating</th>
                        <th class="col-score {{ 'sorted' if sort_by == 'total_score' else '' }}" scope="col">Total Score</th>
                    </tr>
                </thead>
                <tbody>
                {% for player in players %}
                    <tr data-name="{{ player.name }}">
                        <td class="col-rank">
                            {% if player.rank == 1 %}<span class="medal gold" aria-label="rank 1">1</span>
                            {% elif player.rank == 2 %}<span class="medal silver" aria-label="rank 2">2</span>
                            {% elif player.rank == 3 %}<span class="medal bronze" aria-label="rank 3">3</span>
                            {% else %}<span class="rank-num">{{ player.rank }}</span>
                            {% endif %}
                        </td>
                        <td class="col-name">{{ player.name }}</td>
                        <td class="col-rating">{{ '{:,}'.format(player.points) }}</td>
                        <td class="col-score">{{ '{:,}'.format(player.total_score) }}</td>
                    </tr>
                {% endfor %}
                </tbody>
            </table>
        </div>

        <nav class="pager" aria-label="Pagination">
            {% if page > 1 %}
                <a class="pager-btn" rel="prev" href="{{ 'sorted_by_score_page' if sort_by == 'total_score' else 'page' }}{{ page - 1 }}.html">← Previous</a>
            {% else %}
                <span class="pager-btn disabled" aria-disabled="true">← Previous</span>
            {% endif %}
            <span class="pager-info">Page <strong>{{ page }}</strong> of {{ total_pages }}</span>
            {% if page < total_pages %}
                <a class="pager-btn" rel="next" href="{{ 'sorted_by_score_page' if sort_by == 'total_score' else 'page' }}{{ page + 1 }}.html">Next →</a>
            {% else %}
                <span class="pager-btn disabled" aria-disabled="true">Next →</span>
            {% endif %}
        </nav>
    </main>

    <footer class="site-footer">
        <p>Data from <a href="https://thronebutt.com" target="_blank" rel="noopener">thronebutt.com</a> · Built by <a href="https://github.com/senjeyb" target="_blank" rel="noopener">senjeyb</a></p>
        <p>Companion project: <a href="{{ nt_tournament_url }}" target="_blank" rel="noopener">NT: Wasteland Derby — Tournament Stats</a></p>
    </footer>
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


def render(players, page, total_pages, sort_by, total_players, top_name, top_value):
    template = Template(HTML_TEMPLATE)
    return template.render(
        players=players,
        page=page,
        total_pages=total_pages,
        sort_by=sort_by,
        total_players=total_players,
        top_name=top_name,
        top_value=top_value,
        nt_tournament_url=NT_TOURNAMENT_URL,
        icon_base=NT_ICON_BASE,
        players_per_page=PLAYERS_PER_PAGE,
    )


def write_pages(players, sort_by, total_players, top_name, top_value, file_prefix):
    total_pages = max(1, math.ceil(total_players / PLAYERS_PER_PAGE))
    for page in range(1, total_pages + 1):
        start = (page - 1) * PLAYERS_PER_PAGE
        end = start + PLAYERS_PER_PAGE
        page_players = players[start:end]
        html_content = render(page_players, page, total_pages, sort_by, total_players, top_name, top_value)
        with open(f'{file_prefix}{page}.html', 'w', encoding='utf-8') as f:
            f.write(html_content)


if __name__ == '__main__':
    by_rating = fetch_players(order_by='score')
    total_players = len(by_rating)
    top_name_r = by_rating[0]['name'] if by_rating else '—'
    top_value_r = by_rating[0]['points'] if by_rating else 0
    write_pages(by_rating, 'score', total_players, top_name_r, top_value_r, 'page')

    by_killcount = fetch_players(order_by='killcount')
    total_players_k = len(by_killcount)
    top_name_k = by_killcount[0]['name'] if by_killcount else '—'
    top_value_k = by_killcount[0]['total_score'] if by_killcount else 0
    write_pages(by_killcount, 'total_score', total_players_k, top_name_k, top_value_k, 'sorted_by_score_page')

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write('<meta http-equiv="refresh" content="0; URL=page1.html" />')

    with open('sorted_by_score.html', 'w', encoding='utf-8') as f:
        f.write('<meta http-equiv="refresh" content="0; URL=sorted_by_score_page1.html" />')
