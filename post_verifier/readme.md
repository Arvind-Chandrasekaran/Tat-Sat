# Post Verifier 
Verifies the posts queued for creation and then makes database insertion.

Rogue Client Security Compromise
1. Phantom  Media - Media ids sent by the client could be present within the clients media storage. It could never have been uploaded, or client is asking for another user's media.
2. Malicious Media: when file of unknown media type gets uploaded instead of approved an media type to the media object storage. 
3. Orphan Media - Post could be uploaded to a link but not sent back by client with request to /post. This will lead to creation of media that has no post - Storage Garbage Collector. 

"""        
