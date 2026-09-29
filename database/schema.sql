-- Schema for Universal Web Scraper Assignment
-- Database: PostgreSQL

CREATE TABLE IF NOT EXISTS scraped_items (
    id SERIAL PRIMARY KEY,
    source_url TEXT NOT NULL,
    title TEXT,
    description TEXT,
    content TEXT,
    item_type VARCHAR(100) DEFAULT 'generic',
    extra_data JSONB DEFAULT '{}'::jsonb,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_scraped_items_source_url ON scraped_items(source_url);
CREATE INDEX IF NOT EXISTS idx_scraped_items_item_type ON scraped_items(item_type);
CREATE INDEX IF NOT EXISTS idx_scraped_items_scraped_at ON scraped_items(scraped_at DESC);
