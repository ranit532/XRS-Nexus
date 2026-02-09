-- =============================================================================
-- Fabric SQL Endpoint - Analytics Queries
-- Description: Standard T-SQL queries to run against the Lakehouse SQL Endpoint.
-- =============================================================================

-- 1. Total Revenue by Region (Gold Layer)
SELECT 
    c.region,
    SUM(f.amount_usd) as total_revenue,
    COUNT(DISTINCT f.sales_key) as transaction_count
FROM 
    fact_sales f
JOIN 
    dim_customer c ON f.customer_key = c.customer_key
GROUP BY 
    c.region
ORDER BY 
    total_revenue DESC;

-- 2. Top 10 Customers by Revenue
SELECT TOP 10
    c.name,
    SUM(f.amount_usd) as total_spend
FROM 
    fact_sales f
JOIN 
    dim_customer c ON f.customer_key = c.customer_key
GROUP BY 
    c.name
ORDER BY 
    total_spend DESC;

-- 3. Monthly Sales Trend
SELECT 
    FORMAT(s.transaction_date, 'yyyy-MM') as sales_month,
    SUM(s.amount) as monthly_revenue
FROM 
    silver_sales s
GROUP BY 
    FORMAT(s.transaction_date, 'yyyy-MM')
ORDER BY 
    sales_month;

-- 4. Silver vs Gold Data Reconciliation
SELECT 
    (SELECT COUNT(*) FROM silver_sales) as silver_count,
    (SELECT COUNT(*) FROM fact_sales) as gold_count;
