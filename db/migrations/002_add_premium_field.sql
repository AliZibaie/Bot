-- Add is_premium field to users table
ALTER TABLE users 
ADD COLUMN is_premium BOOLEAN NOT NULL DEFAULT FALSE AFTER username,
ADD COLUMN premium_expires_at DATETIME NULL AFTER is_premium;

-- Add index for premium users
CREATE INDEX idx_users_premium ON users(is_premium, premium_expires_at);
