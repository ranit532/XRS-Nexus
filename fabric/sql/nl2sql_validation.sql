-- =============================================================================
-- Fabric SQL Endpoint - NL2SQL Validation
-- Description: Queries to validate AI-generated SQL against known ground truth.
-- =============================================================================

-- Question: "Show me the total sales for Customer 'Acme Corp' in 2024"
-- Expected SQL:
SELECT 
    SUM(s.amount) as total_sales
FROM 
    silver_sales s
JOIN 
    silver_customer c ON s.customer_id = c.customer_id
WHERE 
    c.name = 'Acme Corp' 
    AND YEAR(s.transaction_date) = 2024;

-- Question: "List all inactive customers in the UK"
-- Expected SQL:
SELECT 
    customer_id, 
    name
FROM 
    silver_customer
WHERE 
    country = 'UK' 
    AND is_active = 0; -- Assuming BOOLEAN false is 0 in T-SQL bit

-- Question: "What is the average transaction value per industry?"
-- Expected SQL:
SELECT 
    c.industry,
    AVG(s.amount) as avg_transaction_value
FROM 
    silver_sales s
JOIN 
    silver_customer c ON s.customer_id = c.customer_id
GROUP BY 
    c.industry;
