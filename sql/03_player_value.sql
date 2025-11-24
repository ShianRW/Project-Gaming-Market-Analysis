/*
    File Name: 03_player_value.sql
    Purpose:
        Analyse player value metrics across platforms.
        Focuses on purchase behaviour, owned games, and value segmentation.
    Dataset:
        games_analytics.db (SQLite)
        Tables: players, purchases, games, prices
    Author: Shian Raveneau-Wright
    Notes:
        - Part of the Player Value chapter.
        - Queries support dashboards showing LTV components, like owned game count and spending activity.
*/

/* ===== QUERY 1: Number of Games Owned Per Player ===== */

SELECT
    pl.playerid,
    pl.platform,
    COUNT(pu.gameid) AS games_owned
FROM players AS pl
LEFT JOIN purchases AS pu
    ON pl.playerid = pu.playerid
GROUP BY pl.playerid, pl.platform
ORDER BY games_owned DESC;

/* ===== QUERY 2: Average Games Owned Per Player (Platform Level) ===== */

SELECT
    platform,
    ROUND(AVG(games_owned), 2) AS avg_games_owned
FROM (
    SELECT
        pl.playerid,
        pl.platform,
        COUNT(pu.gameid) AS games_owned
    FROM players AS pl
    LEFT JOIN purchases AS pu
        ON pl.playerid = pu.playerid
    GROUP BY pl.playerid, pl.platform
)
GROUP BY platform
ORDER BY avg_games_owned DESC;

/* ===== QUERY 3: Active Purchasers vs Non-Purchasers ===== */
-- Shows % of players who have made at least one purchase.

SELECT
    platform,
    SUM(CASE WHEN gameid IS NOT NULL THEN 1 ELSE 0 END) AS active_buyers,
    SUM(CASE WHEN gameid IS NULL THEN 1 ELSE 0 END) AS non_buyers,
    ROUND(
        (SUM(CASE WHEN gameid IS NOT NULL THEN 1 ELSE 0 END) * 1.0 
            / COUNT(playerid)) * 100, 2
    ) AS active_buyer_rate
FROM players AS pl
LEFT JOIN purchases AS pu
    ON pl.playerid = pu.playerid
GROUP BY platform
ORDER BY active_buyer_rate DESC;

/* ===== QUERY 4: Estimated Spend Per Player ===== */
-- Estimates spending using game prices at time of acquisition.

WITH player_game_prices AS (
    SELECT
        pl.playerid,
        pl.platform,
        pr.usd AS price_usd
    FROM purchases AS pu
    JOIN players AS pl
        ON pu.playerid = pl.playerid
    JOIN prices AS pr
        ON pu.gameid = pr.gameid
        AND pu.platform = pr.platform
)
SELECT
    platform,
    ROUND(AVG(price_usd), 2) AS avg_spend_per_player_usd,
    ROUND(SUM(price_usd), 2) AS total_revenue_estimate_usd
FROM player_game_prices
GROUP BY platform
ORDER BY avg_spend_per_player_usd DESC;

/* ===== QUERY 5: Player Value Segmentation ===== */
-- Segments players by estimated spend.

WITH player_totals AS (
    SELECT
        pl.playerid,
        pl.platform,
        SUM(pr.usd) AS total_spend
    FROM purchases AS pu
    JOIN players AS pl
        ON pu.playerid = pl.playerid
    JOIN prices AS pr
        ON pu.gameid = pr.gameid
        AND pu.platform = pr.platform
    GROUP BY pl.playerid, pl.platform
)
SELECT
    platform,
    COUNT(CASE WHEN total_spend >= 100 THEN 1 END) AS high_value_players,
    COUNT(CASE WHEN total_spend BETWEEN 30 AND 99 THEN 1 END) AS mid_value_players,
    COUNT(CASE WHEN total_spend < 30 THEN 1 END) AS low_value_players
FROM player_totals
GROUP BY platform
ORDER BY platform;

/* ===== QUERY 6: Country-Level Player Value ===== */
--Shows average player value by country.

WITH player_spend AS (
    SELECT
        pl.playerid,
        pl.country,
        SUM(pr.usd) AS total_spend
    FROM purchases AS pu
    JOIN players AS pl
        ON pu.playerid = pl.playerid
    JOIN prices pr
        ON pu.gameid = pr.gameid
        AND pu.platform = pr.platform
    GROUP BY pl.playerid, pl.country
)
SELECT
    country,
    ROUND(AVG(total_spend), 2) AS avg_spend_per_player,
    ROUND(SUM(total_spend), 2) AS total_country_value
FROM player_spend
GROUP BY country
ORDER BY avg_spend_per_player DESC;


