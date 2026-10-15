import { Post, PostType, SemanticRelationship } from '../types';
import { getAccessToken } from './supabaseClient';

type LogCallback = (msg: string) => void;
const API_URL = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');

export interface QueueResponse {
    status: 'queued';
    message: string;
    queue_id: string;
}

export interface FeedPage {
    feed: Post[];
    next_cursor: string | null;
}

export interface SignedUpload {
    media_id: string;
    path: string;
    signed_url: string;
    token: string;
}

class TatSatBackend {
    private logListeners: LogCallback[] = [];

    public onLog(callback: LogCallback) {
        this.logListeners.push(callback);
        return () => {
            this.logListeners = this.logListeners.filter(listener => listener !== callback);
        };
    }

    private log(message: string) {
        console.log(`[Backend API] ${message}`);
        this.logListeners.forEach(callback => callback(message));
    }

    private async request(path: string, init: RequestInit = {}): Promise<Response> {
        const headers = new Headers(init.headers);
        headers.set('Accept', 'application/json');
        const response = await fetch(`${API_URL}${path}`, { ...init, headers });
        if (!response.ok) {
            const detail = await response.text();
            throw new Error(`API_${response.status}: ${detail || response.statusText}`);
        }
        return response;
    }

    async initialize(onLog?: LogCallback): Promise<void> {
        if (onLog) this.onLog(onLog);
        this.log('Connecting to FastAPI Backend...');
        await this.request('/health');
        this.log('Connected successfully to FastAPI backend.');
    }

    async getFeed(
        filter: 'ALL' | 'HIGH_QUALITY' = 'ALL',
        cursor?: string,
    ): Promise<FeedPage> {
        this.log(`Fetching ${filter === 'HIGH_QUALITY' ? 'high-quality ' : ''}feed...`);
        const params = new URLSearchParams({ filter });
        if (cursor) params.set('cursor', cursor);
        const data = await (await this.request(`/feed?${params}`)).json();
        return {
            feed: (data.feed || []).map((post: Record<string, any>) => this.mapDbPostToType(post)),
            next_cursor: data.next_cursor || null,
        };
    }

    async getSignedUploadUrls(): Promise<SignedUpload[]> {
        const token = await getAccessToken();
        const data = await (await this.request('/post-media-urls', {
            headers: { Authorization: `Bearer ${token}` },
        })).json();
        return data.signed_upload_urls;
    }

    async uploadMedia(file: File, signedUpload: SignedUpload): Promise<void> {
        const response = await fetch(signedUpload.signed_url, {
            method: 'PUT',
            headers: { 'Content-Type': file.type || 'application/octet-stream' },
            body: file,
        });
        if (!response.ok) {
            throw new Error(`MEDIA_UPLOAD_${response.status}: ${await response.text()}`);
        }
    }

    async createPost(text: string, file?: File): Promise<QueueResponse> {
        const token = await getAccessToken();
        let mediaIds: string[] = [];
        let mediaTypes: string[] = [];

        if (file) {
            const [signedUpload] = await this.getSignedUploadUrls();
            await this.uploadMedia(file, signedUpload);
            mediaIds = [signedUpload.media_id];
            mediaTypes = [file.type.split('/')[0] || 'image'];
        }

        this.log('Submitting post for asynchronous verification...');
        const response = await this.request('/post', {
            method: 'POST',
            headers: {
                Authorization: `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text, media_ids: mediaIds, media_types: mediaTypes }),
        });
        const queued = await response.json() as QueueResponse;
        this.log(`Post queued for verification (${queued.queue_id}).`);
        return queued;
    }

    async createComment(_parentId: string, _content: string): Promise<Post> {
        throw new Error('Comments API is not available yet.');
    }

    async getRelatedPosts(_postId: string, _mode: 'DISCOVERY' | 'STRICT'): Promise<{post: Post, score: number, relationship?: SemanticRelationship}[]> {
        return [];
    }

    public async reanalyzeGraph(): Promise<number> {
        this.log('Graph re-analysis is not available yet.');
        return 0;
    }

    private mapDbPostToType(dbPost: Record<string, any>): Post {
        const analysis = dbPost.analysis || { score: 0, scores: {}, toulmin: {}, fallacies: [], grice: {}, sentimentIntensity: 0, reasoning: '', suggestion: '', tags: [], constructive: false };
        return {
            id: `p-${dbPost.id}`,
            author: {
                id: dbPost.user_id || 'unknown',
                name: dbPost.author_name || 'Unknown',
                handle: dbPost.author_handle || 'unknown',
                avatar: dbPost.author_avatar || 'https://via.placeholder.com/50',
                reputationScore: dbPost.author_reputation || 50,
            },
            content: dbPost.text || '',
            type: dbPost.media_type ? PostType.VIDEO : PostType.TEXT,
            mediaUrl: dbPost.media_url,
            thumbnailUrl: dbPost.thumbnail_url,
            analysis,
            topic: dbPost.topic,
            timestamp: new Date(dbPost.created_at),
            likes: dbPost.likes || 0,
            bookmarks: dbPost.bookmarks || 0,
            comments: [],
            relatedPostIds: [],
        };
    }
}

export const backend = new TatSatBackend();
