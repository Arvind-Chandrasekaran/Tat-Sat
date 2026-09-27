
export enum PostType {
  TEXT = 'TEXT',
  VIDEO = 'VIDEO'
}

export type SemanticRelationship = 
  | 'EXPANSION'      // Broadens scope / New domain
  | 'CORROBORATION'  // Adds evidence / Proof
  | 'CHALLENGE'      // Direct disagreement
  | 'NUANCE'         // Limits / Conditions / "Yes, but..."
  | 'SYNTHESIS'      // Combines ideas / Bridge
  | 'PREREQUISITE'   // Foundation / History
  | 'UNCATEGORIZED';

export interface ToulminAnalysis {
  claim: boolean;      // c
  grounds: boolean;    // g
  warrant: boolean;    // w
  backing: boolean;    // b
  qualifier: boolean;  // q
  rebuttal: boolean;   // r
}

export interface GriceAnalysis {
  quality: number;   // MQl
  quantity: number;  // MQn
  relevance: number; // MR
  manner: number;    // MM
}

export interface AnalysisResult {
  score: number; // Final DQS (0-100)
  
  // Component Scores
  scores: {
    ASQ: number; // Argument Structure Quality
    FS: number;  // Fallacy Score
    CPS: number; // Cooperative Principle Score
    ETS: number; // Emotional Tone Score
  };

  // Raw Extraction Data
  toulmin: ToulminAnalysis;
  fallacies: string[]; // List of specific fallacies found
  grice: GriceAnalysis;
  sentimentIntensity: number; // 0 to 1
  
  reasoning: string;
  suggestion: string; // Actionable feedback for the user
  tags: string[];
  constructive: boolean;
  verifiedSources?: { uri: string; title: string }[]; // Google Search Grounding Data
  
  // Persisted Semantic Relationships (Created at post time)
  semanticConnections?: { postId: string; type: SemanticRelationship }[];
}

export interface User {
  id: string;
  name: string;
  handle: string;
  avatar: string;
  reputationScore: number;
}

export interface Post {
  id: string; // Globally unique ID (e.g., "p-1", "c-55")
  parentId?: string; // If present, this is a reply/comment
  rootPostId?: string; // ID of the top-level thread starter
  
  author: User;
  content: string;
  type: PostType;
  
  mediaUrl?: string;
  thumbnailUrl?: string;
  
  analysis: AnalysisResult;
  topic?: string; 
  timestamp: Date;
  
  likes: number; 
  bookmarks: number;
  
  comments: Post[]; // Recursive structure: Comments are just Posts
  
  relatedPostIds?: string[]; 
  embedding?: number[]; 
  topicEmbedding?: number[]; 
}

export enum NavigationTab {
  FEED = 'FEED',
  EXPLORE = 'EXPLORE', 
  CREATE = 'CREATE',
  PROFILE = 'PROFILE'
}
