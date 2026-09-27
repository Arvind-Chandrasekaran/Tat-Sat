# schema : domain

schema namespace : domain

[https://supabase.com/dashboard/project/gsbdwdhzqhvnkylmassr/database/schemas?schema=domain](https://supabase.com/dashboard/project/gsbdwdhzqhvnkylmassr/database/schemas?schema=domain)

### users

Shares a one to one mapping with auth.users

├──id - pk , fk (to auth.users)
├──username - not null, unique, will be reserved forever 
├──status - active, archived (account will be visible posts will be visible, but no more additional posts can be made from that account), deactivated (your media will still be visible; but no one tag you and the posts will not show your name but will show [deactivated]; deleted (1 - only account deleted, posts will be there but will show [deleted], 2 - acount and posts both deleted, the post will show [deleted].)

(username is reserved for 10 years after account is deleted)

users.status enum 

| Status | Public display | Login | Posts |
| --- | --- | --- | --- |
| `active` | `@username` | ✅ | Visible |
| `deactivated` | `[Deactivated User]` | ❌ → can reactivate | Remain |
| `archived` | `@username` | ❌ | Remain |
| `deleted` | `[Deleted User]` | ❌ | Can remain if user chooses |

### posts

├── id - pk
├── user_id - fk domain.users.id
├── text
├── long_text
├── reference_link
├── parent_post_id - fk application.posts.id
├── created_at
├── post_status - active, deleted (post’s content will be removed and replaced with [deleted] default value, but the node will still be there; account is also shown to be deleted when such is the case. Account does not have to be deleted), pending (media approval is awaited), rejected (media approval not given by media verifier, can be removed later by gc).  
└── post_user_visibility - public, private (post’s username should be displayed or not) 

### post_media

├── id
├── created_at
├── post_id
├── media_type
├── storage_path
├── display_order
├── post_media_status - active, rejected, pending 

### post_links

1.  id                                 - PK
2. created_at
3. up_post_id                - FK → [posts.id](http://posts.id/)
4. down_post_id          - FK → [posts.id](http://posts.id/)     (up_post_id , down_post_id) unique 
5. updated_at
6. weight
7. user_count                - Trigger Function that adds the count whenever a new user makes a link and 

### post_links_users

1. link_id       - FK → post_links.id
2. user_id       - FK → [users.id](http://users.id/)
3. created_at
4. PRIMARY KEY (link_id, user_id)