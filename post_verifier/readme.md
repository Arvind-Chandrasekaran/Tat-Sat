"""
Key Notes 

Rogue Client Security 
1 - Malicious file being uplaoded to storage using signed upload url - Proxy Storage and Check magic bytes of the files being uploaded to the storage before approving the post entry in database. 
2 - Phantom  Posts - Post not uploaded by a client could send the media_id as being uploaded - Check the media_ids sent by client. 
3 - Orphan Posts - Post could be uploaded to link but not sent back by client with request to /post. This will lead to creation of media that has no post - Storage Garbage Collector. 

"""        
