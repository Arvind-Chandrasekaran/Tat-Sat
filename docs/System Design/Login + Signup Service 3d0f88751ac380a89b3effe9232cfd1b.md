# Login + Signup Service

schema: domain
table: users 

domain.users has 1:1 mapping with auth.users. 

The domain.users has the following schema  

| id | username | status | created_at |
| --- | --- | --- | --- |
| uuid (foreign key refers aut.users.id) | varchar | active, decativated, deleted, archived |  |

/signup 
auth.user trigger:  will create an corresponding entry in the domain.users. 
The status given will be active and it along with the username will be stored in the column of raw_user_meta_data in auth.users. 
If the username is not present,  email will be used as username. 

| Table | Column | Format | Example |
| --- | --- | --- | --- |
| `auth.users` | `raw_user_meta_data` | JSON/JSONB | `{"username": "krishna123", "status" : "active"}` |