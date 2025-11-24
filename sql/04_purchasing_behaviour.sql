/*
    File Name: 04_purchasing_behaviour.sql
    Purpose:
        Analyse game purchasing behaviour across Steam, PlayStation, and Xbox.
        Focuses on conversion, purchase frequency, velocity, and country-level purchasing patterns.
    Dataset:
        games_analytics.db (SQLite)
        Tables: players, purchases, prices
    Author: Shian Raveneau-Wright
    Notes:
        - Player IDs are platform-specific. No cross-platform comparison of individuals.
        - All comparisons are platform-level, not player-level across platforms.
*/

/* ===== QUERY 1: Initial Purchase Conversion ===== */
-- Percentage of each platform’s players who bought at least 1 game.

SELECT
    pl.platform,
    COUNT(DISTINCT pl.playerid) AS total_players,
    COUNT(DISTINCT pu.playerid) AS players_with_purchase,
    ROUND(
        COUNT(DISTINCT pu.playerid) * 1.0 
        / COUNT(DISTINCT pl.playerid) * 100, 2
    ) AS initial_purchase_conversion_pct
FROM players AS pl
LEFT JOIN purchases AS pu
    ON pl.playerid = pu.playerid
GROUP BY pl.platform
ORDER BY initial_purchase_conversion_pct DESC;

/* ===== QUERY 2: Average Number of Purchases Per Player ===== */

SELECT
    platform,
    ROUND(AVG(purchase_count), 2) AS avg_purchases_per_player
FROM (
    SELECT
        pl.playerid,
        pl.platform,
        COUNT(pu.gameid) AS purchase_count
    FROM players pl
    LEFT JOIN purchases pu
        ON pl.playerid = pu.playerid
    GROUP BY pl.playerid, pl.platform
)
GROUP BY platform
ORDER BY avg_purchases_per_player DESC;

/* ===== QUERY 3: Purchase Velocity (Buyers Only) ===== */
-- Average purchases per buyer (not including non-buyers).
SELECT
    platform,
    ROUND(AVG(purchase_count), 2) AS avg_purchases_per_buyer
FROM (
    SELECT
        pl.playerid,
        pl.platform,
        COUNT(pu.gameid) AS purchase_count
    FROM players pl
    JOIN purchases pu
        ON pl.playerid = pu.playerid
    GROUP BY pl.playerid, pl.platform
)
GROUP BY platform
ORDER BY avg_purchases_per_buyer DESC;

/* ===== QUERY 4: Purchase Frequency Distribution ===== */

WITH player_counts AS ( 
	SELECT
        pl.playerid,
        pl.platform,
        COUNT(pu.gameid) AS purchase_count
    FROM players AS pl
    LEFT JOIN purchases AS pu
        ON pl.playerid = pu.playerid
    GROUP BY pl.playerid, pl.platform
)
SELECT
    platform,
    COUNT(CASE WHEN purchase_count = 0 THEN 1 END) AS zero_purchasers,
    COUNT(CASE WHEN purchase_count BETWEEN 1 AND 10 THEN 1 END) AS low_purchasers,
    COUNT(CASE WHEN purchase_count BETWEEN 11 AND 50 THEN 1 END) AS mid_low_purchasers,
    COUNT(CASE WHEN purchase_count BETWEEN 51 AND 100 THEN 1 END) AS mid_high_purchasers,
    COUNT(CASE WHEN purchase_count > 1001 THEN 1 END) AS high_purchasers
FROM player_counts
GROUP BY platform;

/* ===== QUERY 5: Country-Level Purchase Strength ===== */
-- Shows which geographic markets are most purchase-active.

SELECT
    pl.country,
    pl.platform,
    COUNT(pu.gameid) AS total_purchases,
    ROUND(COUNT(pu.gameid) * 1.0 
        / COUNT(DISTINCT pl.playerid), 2) AS avg_purchases_per_player
FROM players AS pl
LEFT JOIN purchases AS pu
    ON pl.playerid = pu.playerid
GROUP BY pl.country, pl.platform
ORDER BY total_purchases DESC;

/* ===== QUERY 6: Platform Purchasing Summary ===== */
-- Consolidated KPI table for dashboards.

SELECT
    platform,
    COUNT(DISTINCT playerid) AS total_players,
    COUNT(DISTINCT buyerid) AS total_buyers,
    ROUND(COUNT(DISTINCT buyerid) * 100.0 
        / COUNT(DISTINCT playerid), 2) AS conversion_pct,
    ROUND(total_purchases * 1.0 
        / COUNT(DISTINCT buyerid), 2) AS avg_purchases_per_buyer
FROM (
    SELECT
        pl.platform,
        pl.playerid,
        pu.playerid AS buyerid,
        pu.gameid AS purchased_gameid
    FROM players AS pl
    LEFT JOIN purchases AS pu
        ON pl.playerid = pu.playerid
)
GROUP BY platform;
