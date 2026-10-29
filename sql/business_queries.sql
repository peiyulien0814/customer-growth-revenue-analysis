-- SQLite queries; for MySQL change SUBSTR(timestamp,1,7) to DATE_FORMAT(timestamp,'%Y-%m')
-- Monthly sales and average basket size (positive sales only)
SELECT SUBSTR(timestamp,1,7) month, ROUND(SUM(revenue),2) sales_gbp,
       COUNT(DISTINCT invoice) orders,
       ROUND(SUM(revenue)/COUNT(DISTINCT invoice),2) aov_gbp
FROM lines GROUP BY 1 ORDER BY 1;

-- Most valuable products
SELECT stock, MAX(description) product, ROUND(SUM(revenue),2) sales_gbp,
       SUM(quantity) units
FROM lines GROUP BY stock ORDER BY sales_gbp DESC LIMIT 20;

-- Identified-customer frequency / monetary value; no anonymous customers
WITH orders AS (
 SELECT customer, invoice, MIN(timestamp) ts, SUM(revenue) amount
 FROM lines WHERE customer<>'' GROUP BY customer,invoice
)
SELECT customer, COUNT(*) orders, ROUND(SUM(amount),2) monetary_gbp,
       MAX(ts) latest_order
FROM orders GROUP BY customer ORDER BY monetary_gbp DESC LIMIT 50;
