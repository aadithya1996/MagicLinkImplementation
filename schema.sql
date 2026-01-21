-- User Management Schema for Magic Link Authentication

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE magic_links (
    -- Use a secure random string (e.g., usually 32-64 bytes hex)
    token VARCHAR(64) PRIMARY KEY, 
    
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Expiry time (usually created_at + 15 minutes)
    expires_at TIMESTAMP NOT NULL,
    
    -- Prevent replay attacks
    used_at TIMESTAMP, 
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for cleaning up expired tokens
CREATE INDEX idx_magic_links_expires_at ON magic_links(expires_at);
