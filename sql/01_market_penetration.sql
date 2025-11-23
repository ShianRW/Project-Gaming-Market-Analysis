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
FROM players
LEFT JOIN purchases AS pu
    ON pl.playerid = pu.playerid
LEFT JOIN games AS g
    ON pu.gameid = g.gameid 
GROUP BY pl.country, pl.platform
ORDER BY total_players DESC;

/* 
---------------------------------------------------------
Placeholder Section: Next Steps
---------------------------------------------------------
- Market penetration by country
- Market penetration by region
- Cross-platform country comparison
- Penetration normalised by population (optional)
---------------------------------------------------------
*/