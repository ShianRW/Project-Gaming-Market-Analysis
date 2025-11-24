/*
    File Name: 05_top_games.sql
    Purpose:
        Identify top performing games across Steam, PlayStation, and Xbox.
        Analyse purchase volume, top games per platform, cross-platform hits,
        country-specific best sellers, and multi-platform popularity patterns.
    Dataset:
        games_analytics.db (SQLite)
        Tables: players, purchases, games, prices
    Author: Shian Raveneau-Wright
    Notes:
        - Player IDs cannot be compared across platforms.
        - All cross-platform analysis is aggregated at the game level only.
*/

/* ===== QUERY 1: Top Purchased Games Overall ===== */

SELECT
    g.gameid,
    g.title,
    COUNT(pu.gameid) AS total_purchases
FROM purchases AS pu
JOIN games AS g
    ON pu.gameid = g.gameid
GROUP BY g.gameid, g.title
ORDER BY total_purchases DESC;

/* ===== QUERY 2: Top 10 Games Per Platform ===== */

SELECT
    pl.platform,
    g.title,
    COUNT(pu.gameid) AS total_purchases
FROM purchases AS pu
JOIN players AS pl
    ON pu.playerid = pl.playerid
JOIN games g
    ON pu.gameid = g.gameid
GROUP BY pl.platform, g.title
ORDER BY pl.platform, total_purchases DESC
LIMIT 10;

/* ===== QUERY 3: Top 10 Games Per Platform (Window Function) ===== */

WITH game_counts AS (
    SELECT
        pl.platform,
        g.title,
        COUNT(*) AS total_purchases,
        ROW_NUMBER() OVER (
            PARTITION BY pl.platform
            ORDER BY COUNT(*) DESC
        ) AS rn
    FROM purchases AS pu
    JOIN players AS pl ON pu.playerid = pl.playerid
    JOIN games AS g ON pu.gameid = g.gameid
    GROUP BY pl.platform, g.title
)
SELECT platform, title, total_purchases
FROM game_counts
WHERE rn <= 10
ORDER BY platform, total_purchases DESC;

/* ===== QUERY 4: Cross-Platform Hit Titles ===== */
-- Games that sell strongly across multiple ecosystems.

SELECT
    g.title,
    COUNT(DISTINCT pl.platform) AS num_platforms_available,
    COUNT(pu.gameid) AS total_purchases
FROM purchases AS pu
JOIN players AS pl ON pu.playerid = pl.playerid
JOIN games AS g ON pu.gameid = g.gameid
GROUP BY g.title
HAVING num_platforms_available >= 2
ORDER BY total_purchases DESC;

/* ===== QUERY 5: Top Games by Country ===== */

WITH country_games AS (
    SELECT
        pl.country,
        g.title,
        COUNT(*) AS total_purchases,
        ROW_NUMBER() OVER (
            PARTITION BY pl.country
            ORDER BY COUNT(*) DESC
        ) AS rn
    FROM purchases AS pu
    JOIN players AS pl ON pu.playerid = pl.playerid
    JOIN games AS g ON pu.gameid = g.gameid
    GROUP BY pl.country, g.title
)
SELECT country, title, total_purchases
FROM country_games
WHERE rn = 1
ORDER BY total_purchases DESC;

/* ===== QUERY 6: Platform Exclusives ===== */
-- Identifies “ecosystem drivers” — titles that attract customers to one platform.

WITH game_platforms AS (
    SELECT DISTINCT
        g.title,
        pl.platform
    FROM purchases AS pu
    JOIN players AS pl ON pu.playerid = pl.playerid
    JOIN games AS g ON pu.gameid = g.gameid
)
SELECT
    title,
    COUNT(platform) AS platforms_available_on
FROM game_platforms
GROUP BY title
HAVING platforms_available_on = 1;


/* ===== QUERY 7: Estimated Revenue Based on Latest Price Snapshot ===== */

WITH latest_prices AS (
    SELECT
        gameid,
        platform,
        usd,
        ROW_NUMBER() OVER (
            PARTITION BY gameid, platform
            ORDER BY date(date_acquired) DESC
        ) AS rn
    FROM prices
)
SELECT
    g.title,
    pu.platform,
    COUNT(pu.gameid) AS units_sold,
    lp.usd AS latest_price_usd,
    COUNT(pu.gameid) * lp.usd AS estimated_revenue_usd
FROM purchases AS pu
JOIN games AS g ON pu.gameid = g.gameid
JOIN latest_prices AS lp
    ON pu.gameid = lp.gameid
   AND pu.platform = lp.platform
WHERE lp.rn = 1
GROUP BY g.title, pu.platform
ORDER BY estimated_revenue_usd DESC;

/* ===== QUERY 8: Global Estimated Revenue Per Game ===== */

WITH latest_prices AS (
    SELECT
        gameid,
        platform,
        usd,
        ROW_NUMBER() OVER (
            PARTITION BY gameid, platform
            ORDER BY date(date_acquired) DESC
        ) AS rn
    FROM prices
)
SELECT
    g.title,
    SUM(COUNT(pu.gameid) * lp.usd) AS global_estimated_revenue_usd
FROM purchases AS pu
JOIN games AS g ON pu.gameid = g.gameid
JOIN latest_prices AS lp
    ON pu.gameid = lp.gameid
   AND pu.platform = lp.platform
WHERE lp.rn = 1
GROUP BY g.title
ORDER BY global_estimated_revenue_usd DESC;
