/*
    File Name: 01_market_penetration.sql
    Purpose:
        Analyse platform market penetration across global regions.
        Identify which platforms dominate which countries, and how player distribution varies.
    Dataset:
        games_analytics.db (SQLite) — tables: players, games, purchases
    Author: Shian Raveneau-Wright
    Notes:
        - Queries in this file focus on country-level and regional penetration.
        - Outputs will support visualisations for the Market Penetration chapter.
*/

/* Basic platform–country join for market penetration analysis */
SELECT 
    pl.country,
    pl.platform,
    COUNT(pl.playerid) AS total_players
FROM players AS pl
LEFT JOIN purchases AS pu
    ON pl.playerid = pu.playerid
LEFT JOIN games AS g
    ON pu.gameid = g.gameid 
GROUP BY pl.country, pl.platform
ORDER BY total_players DESC;

/* ===== QUERY 1: Total players per country ===== */

SELECT
    country,
    COUNT(playerid) AS total_players
FROM players
GROUP BY country
ORDER BY total_players DESC;

/* ===== QUERY 2: Platform share by country ===== */

SELECT
    country,
    platform,
    COUNT(playerid) AS player_count
FROM players
GROUP BY country, platform
ORDER BY country ASC, player_count DESC;

/* ===== QUERY 3: Country × Platform penetration matrix ===== */

SELECT 
    country,
    SUM(CASE WHEN platform = 'steam' THEN 1 ELSE 0 END) AS steam_players,
    SUM(CASE WHEN platform = 'playstation' THEN 1 ELSE 0 END) AS ps_players,
    SUM(CASE WHEN platform = 'xbox' THEN 1 ELSE 0 END) AS xbox_players
FROM players
GROUP BY country
ORDER BY steam_players DESC;

/* ===== QUERY 4: Top 10 markets by total player count ===== */

SELECT
    country,
    COUNT(playerid) AS total_players
FROM players
GROUP BY country
ORDER BY total_players DESC
LIMIT 10;

/* ===== QUERY 5: Countries with low player penetration ===== */

SELECT
    country,
    COUNT(playerid) AS total_players
FROM players
GROUP BY country
HAVING total_players < 100
ORDER BY total_players ASC;

/* ===== QUERY 6: Market Penetration % (Requires population table) ===== */

-- This will be completed once country populations have been imported into the SQLite database.

-- SELECT 
--     p.country,
--     COUNT(pl.playerid) * 1.0 / pop.population AS penetration_rate
-- FROM players pl
-- JOIN population pop
--     ON pl.country = pop.country
-- GROUP BY p.country;