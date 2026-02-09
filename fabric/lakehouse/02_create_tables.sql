-- =============================================================================
-- Fabric Lakehouse - Lakehouse Schema DDL
-- Description: Creates managed Delta tables for Silver and Gold layers.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Silver Layer (Cleaned Data)
-- -----------------------------------------------------------------------------

-- Customer Master (Unified)
CREATE TABLE IF NOT EXISTS silver_customer (
    customer_id STRING,
    source_system STRING, -- 'SAP', 'SFDC'
    source_id STRING,
    name STRING,
    region STRING,
    country STRING,
    industry STRING,
    ingestion_timestamp TIMESTAMP,
    is_active BOOLEAN
) USING DELTA;

-- Sales Transactions
CREATE TABLE IF NOT EXISTS silver_sales (
    transaction_id STRING,
    customer_id STRING,
    product_id STRING,
    amount DECIMAL(18, 2),
    currency STRING,
    transaction_date DATE,
    status STRING
) USING DELTA;

-- -----------------------------------------------------------------------------
-- Gold Layer (Star Schema for Power BI DirectLake)
-- -----------------------------------------------------------------------------

-- Dimension: Customer
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_key LONG, -- Surrogate Key
    customer_id STRING,
    name STRING,
    region STRING,
    country STRING,
    current_flag BOOLEAN,
    effective_start_date DATE,
    effective_end_date DATE
) USING DELTA;

-- Fact: Sales
CREATE TABLE IF NOT EXISTS fact_sales (
    sales_key LONG,
    customer_key LONG,
    product_key LONG,
    date_key LONG,
    amount_usd DECIMAL(18, 2),
    quantity INT
) USING DELTA;

-- -----------------------------------------------------------------------------
-- Optimization (V-Order & Maintenance)
-- -----------------------------------------------------------------------------

-- Run these periodically via Notebook or SQL Job
-- OPTIMIZE silver_customer VORDER;
-- OPTIMIZE fact_sales VORDER ZORDER BY (date_key);
