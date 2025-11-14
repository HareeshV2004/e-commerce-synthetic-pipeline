/*
 * Customer-Product Analysis Query
 * 
 * This query joins customers, orders, order_items, products, and shipments
 * to produce an aggregated view of customer-product relationships showing:
 * - Customer information (id, name, country)
 * - Product information (id, name, category)
 * - Total quantity purchased
 * - Total revenue (quantity * item_price)
 * - Number of orders containing this product
 * - First and most recent order dates
 * - Total shipment costs for orders containing this product
 * 
 * Results are ordered by total revenue descending, limited to top 100.
 */

SELECT 
    -- Customer information
    c.customer_id,
    c.first_name,
    c.last_name,
    c.country,
    
    -- Product information
    p.product_id,
    p.name AS product_name,
    p.category,
    
    -- Aggregated metrics
    SUM(oi.quantity) AS total_quantity,
    SUM(oi.quantity * oi.item_price) AS total_revenue,
    COUNT(DISTINCT oi.order_id) AS number_of_orders,
    MIN(o.order_date) AS first_order_date,
    MAX(o.order_date) AS most_recent_order_date,
    -- Calculate total shipment cost by joining with aggregated shipment costs per order
    COALESCE(SUM(order_shipments.total_shipment_cost), 0) AS total_shipment_cost

FROM 
    -- Start with customers table
    customers c
    
    -- Join orders to get customer orders
    INNER JOIN orders o 
        ON c.customer_id = o.customer_id
    
    -- Join order_items to get product details for each order
    INNER JOIN order_items oi 
        ON o.order_id = oi.order_id
    
    -- Join products to get product information
    INNER JOIN products p 
        ON oi.product_id = p.product_id
    
    -- Left join with subquery that aggregates shipment costs per order
    -- This prevents double-counting when orders have multiple shipments
    LEFT JOIN (
        SELECT 
            order_id,
            SUM(shipment_cost) AS total_shipment_cost
        FROM shipments
        GROUP BY order_id
    ) order_shipments 
        ON o.order_id = order_shipments.order_id

-- Group by customer and product to aggregate at customer-product level
GROUP BY 
    c.customer_id,
    c.first_name,
    c.last_name,
    c.country,
    p.product_id,
    p.name,
    p.category

-- Order by total revenue descending (highest revenue first)
ORDER BY 
    total_revenue DESC

-- Limit to top 100 customer-product pairs by revenue
LIMIT 100;

