/*
    File Name: 02_acquisition_growth.sql
    Purpose:
        Analyse player acquisition growth over time (month, quarter, YoY).
        Identify trends, growth spikes, seasonal patterns, and platform differences.
    Dataset:
        games_analytics.db (SQLite) — players table (created_date column required)
    Author: Shian Raveneau-Wright
    Notes:
        - This script builds directly on insights from market penetration.
        - Queries here are intended for visualisation (line charts, bar charts, CAGR).
*/

/* === TEMPORARY VIEW: Players with date components === */
CREATE VIEW IF NOT EXISTS players_enriched AS
SELECT
    playerid,
    platform,
    country,
    created_date,
    STRFTIME('%Y', created_date) AS year,
    STRFTIME('%m', created_date) AS month,
    'Q' || ((CAST(STRFTIME('%m', created_date) AS INTEGER) - 1) / 3 + 1) AS quarter
FROM players;

/* ===== QUERY 1: Total Gamers Added Per Month (Global) ===== */

SELECT
    year,
    month,
    COUNT(playerid) AS new_players
FROM players_enriched
GROUP BY year, month
ORDER BY year ASC, month ASC;

/* ===== QUERY 2: Total Gamers Added Per Quarter ===== */

SELECT
    year,
    quarter,
    COUNT(playerid) AS new_players
FROM players_enriched
GROUP BY year, quarter
ORDER BY year ASC, quarter ASC;

/* ===== QUERY 3: Total Gamers Added Per Year ===== */

SELECT
    year,
    COUNT(playerid) AS new_players
FROM players_enriched
GROUP BY year
ORDER BY year ASC;

/* ===== QUERY 4: Platform Growth Per Month ===== */

SELECT
    year,
    month,
    platform,
    COUNT(playerid) AS new_players
FROM players_enriched
GROUP BY year, month, platform
ORDER BY year ASC, month ASC, platform ASC;

/* ===== QUERY 5: Platform Growth Per Quarter ===== */

SELECT
    year,
    quarter,
    platform,
    COUNT(playerid) AS new_players
FROM players_enriched
GROUP BY year, quarter, platform
ORDER BY year ASC, quarter ASC, platform ASC;

/* ===== QUERY 6: Platform Growth Per Year ===== */

SELECT
    year,
    platform,
    COUNT(playerid) AS new_players
FROM players_enriched
GROUP BY year, platform
ORDER BY year ASC, platform ASC;

/* ===== QUERY 7: Market Growth Contribution by Platform ===== */

WITH yearly_totals AS (
    SELECT
        year,
        COUNT(playerid) AS total_players
    FROM players_enriched
    GROUP BY year
),
platform_yearly AS (
    SELECT
        year,
        platform,
        COUNT(playerid) AS platform_players
    FROM players_enriched
    GROUP BY year, platform
)
SELECT
    py.year,
    py.platform,
    py.platform_players,
    yt.total_players,
    ROUND(
        (py.platform_players * 1.0 / yt.total_players) * 100,
        2
    ) AS contribution_percentage
FROM platform_yearly py
JOIN yearly_totals yt USING (year)
ORDER BY py.year ASC, contribution_percentage DESC;

/* ===== QUERY 8: Unified Growth Table (Year × Platform + Totals) ===== */

SELECT
    year,
    SUM(CASE WHEN platform = 'steam' THEN 1 ELSE 0 END) AS steam_new,
    SUM(CASE WHEN platform = 'playstation' THEN 1 ELSE 0 END) AS ps_new,
    SUM(CASE WHEN platform = 'xbox' THEN 1 ELSE 0 END) AS xbox_new,
    COUNT(playerid) AS total_new_players
FROM players_enriched
GROUP BY year
ORDER BY year ASC;