What are the top 5 brands by receipts scanned for most recent month?
Query:
select distinct br.name as brand_name, r.date_scanned  from receipts r join receipt_items ri on r.receipt_id = ri.receipt_id join brands br on ri.barcode = br.barcode where br.top_brand = true order by r.date_scanned desc limit 5;

WITH receipt_month AS ( select distinct receipt_id, EXTRACT(MONTH FROM date_scanned) as month from receipts order by month desc )
select distinct br.name as brand_name, r.month from receipt_month r join receipt_items ri on r.receipt_id = ri.receipt_id join brands br on ri.barcode = br.barcode where br.top_brand = true order by r.month desc limit 5;


gpt:
WITH recent_month AS (
    -- Find the most recent month in the receipts table
    SELECT MAX(date_scanned) AS max_date
    FROM receipts
),
monthly_receipts AS (
    -- Select receipts scanned in the most recent month
    SELECT distinct receipt_id
    FROM receipts
    WHERE EXTRACT(MONTH FROM date_scanned) = EXTRACT(MONTH FROM (SELECT max_date FROM recent_month))
),
brand_barcode_counts AS (
    -- Count the number of receipts for each brand in the most recent month
    SELECT distinct
        b.brand_id,
        b.name AS brand_name,
        COUNT(DISTINCT ri.barcode) AS barcode_count
    FROM
        monthly_receipts mr
        JOIN receipt_items ri ON mr.receipt_id = ri.receipt_id
        JOIN brands b ON ri.barcode = b.barcode
    GROUP BY
        b.brand_id, b.name
)
-- Select the top 5 brands by receipt count
SELECT
    brand_id,
    brand_name,
    barcode_count
FROM
    brand_barcode_counts
ORDER BY
    barcode_count DESC
LIMIT 5;

---------------------
WITH brand_barcode_counts AS (
    -- Count the number of receipts for each brand in the most recent month
    SELECT distinct
        b.brand_id,
        b.name AS brand_name,
        COUNT(DISTINCT ri.barcode) AS barcode_count
    FROM
        receipts mr
        JOIN receipt_items ri ON mr.receipt_id = ri.receipt_id
        JOIN brands b ON ri.barcode = b.barcode
    GROUP BY
        b.brand_id, b.name
)
SELECT
    brand_id,
    brand_name,
    barcode_count
FROM
    brand_barcode_counts
ORDER BY
    barcode_count DESC
LIMIT 5;
---------------------

2) How does the ranking of the top 5 brands by receipts scanned for the recent month compare to the ranking for the previous month?

WITH month_data AS (
    SELECT DISTINCT EXTRACT(MONTH FROM date_scanned) AS month
    FROM receipts
    ORDER BY month DESC
    LIMIT 2
),
recent_month AS (
    SELECT month AS recent_month
    FROM month_data
    ORDER BY month DESC
    LIMIT 1
),
previous_month AS (
    SELECT month AS previous_month
    FROM month_data
    ORDER BY month DESC
    OFFSET 1
    LIMIT 1
),
recent_month_receipts AS (
    SELECT receipt_id
    FROM receipts
    WHERE EXTRACT(MONTH FROM date_scanned) = (SELECT recent_month FROM recent_month)
),
previous_month_receipts AS (
    SELECT receipt_id
    FROM receipts
    WHERE EXTRACT(MONTH FROM date_scanned) = (SELECT previous_month FROM previous_month)
),
recent_month_counts AS (
    SELECT
        b.brand_id,
        b.name AS brand_name,
        COUNT(DISTINCT rmr.receipt_id) AS receipt_count,
        RANK() OVER (ORDER BY COUNT(DISTINCT rmr.receipt_id) DESC) AS rank
    FROM
        recent_month_receipts rmr
        JOIN receipt_items ri ON rmr.receipt_id = ri.receipt_id
        JOIN brands b ON ri.barcode = b.barcode
    GROUP BY
        b.brand_id, b.name
    ORDER BY
        rank
    LIMIT 5
),
previous_month_counts AS (
    SELECT
        b.brand_id,
        b.name AS brand_name,
        COUNT(DISTINCT pmr.receipt_id) AS receipt_count,
        RANK() OVER (ORDER BY COUNT(DISTINCT pmr.receipt_id) DESC) AS rank
    FROM
        previous_month_receipts pmr
        JOIN receipt_items ri ON pmr.receipt_id = ri.receipt_id
        JOIN brands b ON ri.barcode = b.barcode
    GROUP BY
        b.brand_id, b.name
    ORDER BY
        rank
    LIMIT 5
)
SELECT
    recent.brand_id,
    recent.brand_name,
    recent.receipt_count AS recent_month_receipt_count,
    recent.rank AS recent_month_rank,
    previous.receipt_count AS previous_month_receipt_count,
    previous.rank AS previous_month_rank
FROM
    recent_month_counts recent
    LEFT JOIN previous_month_counts previous ON recent.brand_id = previous.brand_id
UNION ALL
SELECT
    previous.brand_id,
    previous.brand_name,
    NULL AS recent_month_receipt_count,
    NULL AS recent_month_rank,
    previous.receipt_count AS previous_month_receipt_count,
    previous.rank AS previous_month_rank
FROM
    previous_month_counts previous
    LEFT JOIN recent_month_counts recent ON previous.brand_id = recent.brand_id
WHERE
    recent.brand_id IS NULL
ORDER BY
    recent_month_rank, previous_month_rank;



3) When considering average spend from receipts with 'rewardsReceiptStatus’ of ‘Accepted’ or ‘Rejected’, which is greater?

SELECT
    rewards_receipt_status,
    AVG(total_spent) AS average_spend
FROM
    receipts
WHERE
    rewards_receipt_status IN ('FINISHED', 'REJECTED')
GROUP BY
    rewards_receipt_status;


4) When considering total number of items purchased from receipts with 'rewardsReceiptStatus’ of ‘Accepted’ or ‘Rejected’, which is greater?

SELECT
    rewards_receipt_status,
    SUM(purchased_item_count) AS total_items_purchased
FROM
    receipts
WHERE
    rewards_receipt_status IN ('FINISHED', 'REJECTED')
GROUP BY
    rewards_receipt_status;


select distinct create_date, date_Scanned, finished_date, modify_date, points_awarded_date, purchase_date from receipts

5) Which brand has the most spend among users who were created within the past 6 months?

WITH max_created_date AS (
    -- Find the most recent created_date
    SELECT MAX(created_date) AS max_date
    FROM users
),
recent_users AS (
    -- Select users created within 6 months from the most recent created_date
    SELECT user_id
    FROM users
    WHERE created_date >= (SELECT max_date FROM max_created_date) - INTERVAL '6 months'
),
user_receipts AS (
    -- Select receipts from the recent users
    SELECT r.receipt_id, r.total_spent, ri.barcode
    FROM receipts r
    JOIN recent_users ru ON r.user_id = ru.user_id
    JOIN receipt_items ri ON r.receipt_id = ri.receipt_id
),
brand_spend AS (
    -- Calculate the total spend for each brand by recent users
    SELECT b.brand_id, b.name AS brand_name, SUM(ur.total_spent) AS total_spent
    FROM user_receipts ur
    JOIN brands b ON ur.barcode = b.barcode
    GROUP BY b.brand_id, b.name
)
-- Select the brand with the highest total spend
SELECT brand_id, brand_name, total_spent
FROM brand_spend
ORDER BY total_spent DESC

6) Which brand has the most transactions among users who were created within the past 6 months?

WITH max_created_date AS (
    -- Find the most recent created_date
    SELECT MAX(created_date) AS max_date
    FROM users
),
recent_users AS (
    -- Select users created within 6 months from the most recent created_date
    SELECT user_id
    FROM users
    WHERE created_date >= (SELECT max_date FROM max_created_date) - INTERVAL '6 months'
),
user_receipts AS (
    -- Select receipts from the recent users
    SELECT r.receipt_id, ri.barcode
    FROM receipts r
    JOIN recent_users ru ON r.user_id = ru.user_id
    JOIN receipt_items ri ON r.receipt_id = ri.receipt_id
),
brand_transactions AS (
    -- Calculate the total number of transactions for each brand by recent users
    SELECT b.brand_id, b.name AS brand_name, COUNT(ur.receipt_id) AS transaction_count
    FROM user_receipts ur
    JOIN brands b ON ur.barcode = b.barcode
    GROUP BY b.brand_id, b.name
)
-- Select the brand with the highest number of transactions
SELECT brand_id, brand_name, transaction_count
FROM brand_transactions
ORDER BY transaction_count DESC
LIMIT 1;


WITH recent_month AS (
    -- Find the most recent month in the receipts table
    SELECT MAX(date_scanned) AS max_date
    FROM receipts
),
monthly_receipts AS (
    -- Select receipts scanned in the most recent month
    SELECT receipt_id
    FROM receipts
    WHERE date_trunc('month', date_scanned) = date_trunc('month', (SELECT max_date FROM recent_month))
),
bar_code AS 
(SELECT
        ri.barcode,
        COUNT(DISTINCT ri.receipt_id) AS receipt_count
    FROM
        monthly_receipts mr
        JOIN receipt_items ri ON mr.receipt_id = ri.receipt_id
    GROUP BY ri.barcode
) SELECT 
        b.name,
        b.barcode
    FROM
    bar_code br
    JOIN brands b ON b.barcode = br.barcode
    GROUP BY b.name, b.barcode;

    SELECT * FROM brands WHERE barcode = "B076FJ92M4"

    SELECT COUNT (*) FROM brands b JOIN receipt_items r ON r.barcode = b.barcode ;