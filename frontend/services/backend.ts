import { Post, PostType, AnalysisResult, SemanticRelationship } from '../types';

type LogCallback = (msg: string) => void;

// Assuming backend runs on 8000
const API_URL = 'http://127.0.0.1:8000';

class TatSatBackend {
    
    private logListeners: LogCallback[] = [];

    // Helpers to handle ID Namespacing
    private toPostId(dbId: string | number) { return `p-${dbId}`; }
    private toCommentId(dbId: string | number) { return `c-${dbId}`; }
    private fromId(appId: string) { return appId.split('-')[1]; }

    public onLog(callback: LogCallback) {
        this.logListeners.push(callback);
    }

    private log(msg: string) {
        console.log(`[Backend API] ${msg}`);
        this.logListeners.forEach(cb => cb(msg));
    }

    async initialize(onLog?: (msg: string) => void): Promise<void> {
        if(onLog) this.onLog(onLog);
        this.log("Connecting to FastAPI Backend...");
        
        try {
            const res = await fetch(`${API_URL}/health`);
            if (!res.ok) throw new Error("Connection Failed");
            this.log("Connected successfully to FastAPI backend.");
        } catch (e) {
            this.log(`Connection Error: ${e}`);
            throw new Error("CONNECTION_FAILED");
        }
    }

    async getFeed(filter: 'ALL' | 'HIGH_QUALITY' = 'ALL'): Promise<Post[]> {
        this.log("Fetching Feed...");
        const res = await fetch(`${API_URL}/feed?filter=${filter}`);
        if (!res.ok) throw new Error("Failed to fetch feed");
        const data = await res.json();
        
        const posts = (data.feed || []).map((dbPost: any) => this.mapDbPostToType(dbPost));
        return posts;
    }

    async createPost(content: string, type: PostType, mediaUrl?: string): Promise<void> {
        this.log("Delegating Post Creation and AI Analysis to Backend...");
        
        const res = await fetch(`${API_URL}/post`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                // Dummy JWT for now since the frontend logic hasn't fully updated to proper auth flow
                // The router expects a bearer token. We will send a mock token that the custom JWTManager might accept, 
                // but since JWTManager expects a valid token, we might need to bypass it or provide a valid signed token.
                // Assuming the backend has a way to handle this or we can adjust router if it fails.
                "Authorization": "Bearer MOCK_TOKEN_FOR_DEV" 
            },
            body: JSON.stringify({
                content,
                type,
                media_url: mediaUrl,
                media_ids: [],
                media_types: []
            })
        });

        if (!res.ok) {
            const err = await res.text();
            throw new Error(`Failed to create post: ${err}`);
        }
        this.log("Post created and analyzed successfully by backend.");
    }

    async createComment(parentId: string, content: string): Promise<Post> {
         throw new Error("Not Implemented in this merge iteration.");
    }

    async getRelatedPosts(postId: string, mode: 'DISCOVERY' | 'STRICT'): Promise<{post: Post, score: number, relationship?: SemanticRelationship}[]> {
        // Mocked or fetching from backend
        return [];
    }

    public async reanalyzeGraph(): Promise<number> {
        this.log("Reanalyze graph is now a backend responsibility.");
        return 0;
    }

    private mapDbPostToType(dbPost: any): Post {
        let emb = dbPost.embedding;
        if (typeof emb === 'string') {
            try { emb = JSON.parse(emb); } catch { emb = undefined; }
        }

        return {
            id: this.toPostId(dbPost.id),
            author: {
                id: dbPost.author_id || 'unknown',
                name: dbPost.author_name || 'Unknown',
                handle: dbPost.author_handle || 'unknown',
                avatar: dbPost.author_avatar || 'https://via.placeholder.com/50',
                reputationScore: dbPost.author_reputation || 50
            },
            content: dbPost.content,
            type: dbPost.type as PostType,
            mediaUrl: dbPost.media_url,
            thumbnailUrl: dbPost.thumbnail_url,
            analysis: dbPost.analysis,
            topic: dbPost.topic,
            timestamp: new Date(dbPost.created_at),
            likes: dbPost.likes,
            bookmarks: dbPost.bookmarks,
            comments: dbPost.comments 
                ? dbPost.comments.map((c: any) => this.mapDbCommentToType(c)) 
                : [],
            relatedPostIds: [],
            embedding: emb || undefined,
            topicEmbedding: dbPost.topic_embedding || undefined
        };
    }

    private mapDbCommentToType(dbComment: any): Post {
        return {
            id: this.toCommentId(dbComment.id),
            parentId: this.toPostId(dbComment.post_id),
            author: { 
                id: dbComment.author_id, 
                name: dbComment.author_name, 
                handle: dbComment.author_handle, 
                avatar: dbComment.author_avatar, 
                reputationScore: 50 
            },
            content: dbComment.content,
            type: PostType.TEXT,
            timestamp: new Date(dbComment.created_at),
            analysis: dbComment.analysis,
            likes: dbComment.likes,
            bookmarks: 0,
            comments: [] 
        };
    }
}

export const backend = new TatSatBackend();
