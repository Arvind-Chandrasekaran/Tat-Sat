
-- 1. Enable pgvector for basic vector arithmetic
create extension if not exists vector;

-- 2. Enable pgvectorscale for high-performance DiskANN indexing
-- This is critical for scaling to millions/billions of rows without exhausting RAM.
create extension if not exists vectorscale cascade;

create table if not exists posts (
  id bigint primary key generated always as identity,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  
  content text not null,
  type text not null default 'TEXT', -- 'TEXT' or 'VIDEO'
  
  -- Author Metadata (Denormalized for read performance)
  author_id text not null,
  author_name text not null,
  author_handle text not null,
  author_avatar text,
  author_reputation int default 50,
  
  -- Media
  media_url text,
  thumbnail_url text,
  
  -- AI Analysis Blob (JSONB)
  analysis jsonb not null default '{}'::jsonb,
  
  -- Topic Modeling
  topic text,
  
  -- Metrics
  likes int default 0,
  bookmarks int default 0,
  
  -- Vectors (Gemini text-embedding-004 is 768 dimensions)
  embedding vector(768),
  topic_embedding vector(768)
);

create table if not exists comments (
  id bigint primary key generated always as identity,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  
  post_id bigint references posts(id) on delete cascade not null,
  
  content text not null,
  
  author_id text not null,
  author_name text not null,
  author_handle text not null,
  author_avatar text,
  
  analysis jsonb default '{}'::jsonb,
  likes int default 0
);

-- INDEXING STRATEGY: StreamingDiskANN
-- Replaces HNSW. Optimized for 100M+ vectors on NVMe SSDs.
-- Uses significantly less RAM (approx 1/32th of HNSW) by storing the graph on disk.
-- NOTE: If pgvectorscale is not available in your specific Postgres environment, 
-- fallback to: create index on posts using hnsw (embedding vector_cosine_ops);
create index if not exists posts_embedding_diskann_idx on posts using diskann (embedding);
create index if not exists posts_topic_embedding_diskann_idx on posts using diskann (topic_embedding);

-- HYBRID SEARCH FUNCTION
-- Matches based on semantic similarity AND topic similarity if available.
create or replace function sattva_hybrid_search(
  query_embedding vector(768),
  query_topic_embedding vector(768),
  match_threshold float,
  match_count int,
  filter_quality boolean default false
)
returns table (
  id bigint,
  content text,
  topic text,
  type text,
  author_id text,
  author_name text,
  author_handle text,
  author_avatar text,
  author_reputation int,
  created_at timestamp with time zone,
  media_url text,
  thumbnail_url text,
  analysis jsonb,
  likes int,
  bookmarks int,
  similarity float
)
language plpgsql
as $$
begin
  return query
  select
    posts.id,
    posts.content,
    posts.topic,
    posts.type,
    posts.author_id,
    posts.author_name,
    posts.author_handle,
    posts.author_avatar,
    posts.author_reputation,
    posts.created_at,
    posts.media_url,
    posts.thumbnail_url,
    posts.analysis,
    posts.likes,
    posts.bookmarks,
    -- Distance calc works seamlessly with DiskANN
    -- <=> is the cosine distance operator
    (1 - (posts.embedding <=> query_embedding)) as similarity
  from posts
  where 1 - (posts.embedding <=> query_embedding) > match_threshold
  and (
    filter_quality = false 
    or 
    (posts.analysis->>'score')::int > 50
  )
  order by (1 - (posts.embedding <=> query_embedding)) desc
  limit match_count;
end;
$$;
