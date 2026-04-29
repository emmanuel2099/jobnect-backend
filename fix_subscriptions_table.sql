-- Add missing jobs_applied column to subscriptions table
ALTER TABLE subscriptions 
ADD COLUMN IF NOT EXISTS jobs_applied INTEGER DEFAULT 0;

-- Verify the column was added
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'subscriptions' 
AND column_name = 'jobs_applied';
