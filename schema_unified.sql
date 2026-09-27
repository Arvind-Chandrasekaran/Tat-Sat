-- Enable Vector Extensions
create extension if not exists vector;
create extension if not exists vectorscale cascade;

-- Create Domain Schema
create schema if not exists domain;

-- 1. USERS (1:1 with auth.users)
create table if not exists domain.users (
  id uuid primary key references auth.users(id) on delete cascade,
  username varchar not null unique,
  status varchar not null default 'active', -- active, archived, deactivated, deleted
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 2. POSTS
create table if not exists domain.posts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references domain.users(id) not null,
  text varchar(560) not null, -- Enforced 560 max derived from PDF
  long_text text,
  reference_link text,
  parent_post_id uuid references domain.posts(id),
  
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  post_status varchar not null default 'pending', -- active, deleted, pending, rejected
  post_user_visibility varchar not null default 'public', -- public, private
  
  -- AI Integration Fields
  analysis jsonb not null default '{}'::jsonb,
  topic text,
  embedding vector(768),
  topic_embedding vector(768),
  likes int default 0,
  bookmarks int default 0
);

-- Indexing for AI
create index if not exists posts_embedding_diskann_idx on domain.posts using diskann (embedding);
create index if not exists posts_topic_embedding_diskann_idx on domain.posts using diskann (topic_embedding);

-- 3. POST MEDIA
create table if not exists domain.post_media (
  id uuid primary key default gen_random_uuid(),
  post_id uuid references domain.posts(id) not null,
  media_type varchar not null, -- image, video, audio
  storage_path text not null,
  display_order int not null,
  post_media_status varchar not null default 'pending', -- active, rejected, pending
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 4. POST LINKS (Crowdsourced Knowledge Graph)
create table if not exists domain.post_links (
  id uuid primary key default gen_random_uuid(),
  up_post_id uuid references domain.posts(id) not null,
  down_post_id uuid references domain.posts(id) not null,
  weight int default 1,
  user_count int default 0,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
  unique(up_post_id, down_post_id)
);

-- 5. POST LINKS USERS (Attribution)
create table if not exists domain.post_links_users (
  link_id uuid references domain.post_links(id) not null,
  user_id uuid references domain.users(id) not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  primary key (link_id, user_id)
);

-- 6. HYBRID SEARCH RPC (Updated for domain schema)
create or replace function domain.sattva_hybrid_search(
  query_embedding vector(768),
  query_topic_embedding vector(768),
  match_threshold float,
  match_count int,
  filter_quality boolean default false
)
returns table (
  id uuid,
  text varchar(560),
  topic text,
  user_id uuid,
  created_at timestamp with time zone,
  analysis jsonb,
  similarity float
)
language plpgsql
as $$
begin
  return query
  select
    posts.id,
    posts.text,
    posts.topic,
    posts.user_id,
    posts.created_at,
    posts.analysis,
    (1 - (posts.embedding <=> query_embedding)) as similarity
  from domain.posts as posts
  where 1 - (posts.embedding <=> query_embedding) > match_threshold
  and posts.post_status = 'active'
  and (
    filter_quality = false 
    or 
    (posts.analysis->>'score')::int > 50
  )
  order by (1 - (posts.embedding <=> query_embedding)) desc
  limit match_count;
end;
$$;
