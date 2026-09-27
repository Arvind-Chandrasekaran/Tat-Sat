# Post Creation Service

### Overview

This server provides end-points that allow a logged in user client to create a post. 

This service follows the ‘direct-to-storage’ upload architecture, where the user client will directly upload the media to object storage (if their posts contains a media) using the /post-media-urls end-point and then create a database entry contains the textual data along with media files location details for the post using the /post end-point.

### API Reference

[https://postcreationservice-production.up.railway.app/api-reference](https://postcreationservice-production.up.railway.app/api-reference)

Deployment URL - [https://postcreationservice-production.up.railway.app/](https://postcreationservice-production.up.railway.app/api-reference)

### Performance Benchmarking

| Concurrent Virtual Users | Throughput (req/s) | p50 / Median | p90 | **p95** | Max | HTTP failures |
| --- | --- | --- | --- | --- | --- | --- |
| **50** | **26.92** | **593.8 ms** | 963 ms | **1.06 s** | 1.84 s | **0%** |
| **100** | **36.20** | **1.07 s** | 2.10 s | **2.45 s** | ~? | **0%** |
| **150** | **39.70** | **1.17 s** | 2.86 s | **3.42 s** | ~? | **0%** |
| **200** | **40.66** | **1.50 s** | 3.74 s | **4.64 s** | **11.89 s** | **0%** |