
import { GoogleGenAI, Type, Schema, GenerateContentResponse, EmbedContentResponse, EmbedContentRequest } from "@google/genai";
import { AnalysisResult, ToulminAnalysis, GriceAnalysis, SemanticRelationship } from "../types";

const apiKey = process.env.API_KEY || '';

// Initialize client ONLY if key exists
const ai = apiKey ? new GoogleGenAI({ apiKey }) : null;

export const isAIConfigured = () => !!ai;

// Helper to prevent hanging requests
const withTimeout = <T>(promise: Promise<T>, ms: number = 600000): Promise<T> => { // Default 10 mins
    return Promise.race([
        promise,
        new Promise<T>((_, reject) => setTimeout(() => reject(new Error("AI Request Timed Out")), ms))
    ]);
};

// --- SCHEMAS FOR EXTRACTION ---

const analysisSchema: Schema = {
  type: Type.OBJECT,
  properties: {
    toulmin: {
      type: Type.OBJECT,
      description: "Structure",
      properties: {
        claim: { type: Type.BOOLEAN },
        grounds: { type: Type.BOOLEAN },
        warrant: { type: Type.BOOLEAN },
        backing: { type: Type.BOOLEAN },
        qualifier: { type: Type.BOOLEAN },
        rebuttal: { type: Type.BOOLEAN },
      },
      required: ["claim", "grounds", "warrant", "backing", "qualifier", "rebuttal"]
    },
    fallacies: {
      type: Type.ARRAY,
      items: { type: Type.STRING },
      description: "Detected fallacies.",
    },
    grice: {
      type: Type.OBJECT,
      description: "Scores 0.0-1.0",
      properties: {
        quality: { type: Type.NUMBER },
        quantity: { type: Type.NUMBER },
        relevance: { type: Type.NUMBER },
        manner: { type: Type.NUMBER },
      },
      required: ["quality", "quantity", "relevance", "manner"]
    },
    sentimentIntensity: { type: Type.NUMBER },
    reasoning: { type: Type.STRING },
    suggestion: { type: Type.STRING },
    tags: { type: Type.ARRAY, items: { type: Type.STRING } },
    constructive: { type: Type.BOOLEAN }
  },
  required: ["toulmin", "fallacies", "grice", "sentimentIntensity", "reasoning", "suggestion", "tags", "constructive"],
};

const commentTopicsSchema: Schema = {
  type: Type.OBJECT,
  properties: {
    mappings: {
      type: Type.ARRAY,
      items: {
        type: Type.OBJECT,
        properties: { id: { type: Type.STRING }, topic: { type: Type.STRING } },
        required: ["id", "topic"]
      }
    }
  },
  required: ["mappings"]
};

const singleTopicSchema: Schema = {
  type: Type.OBJECT,
  properties: { topic: { type: Type.STRING } },
  required: ["topic"]
};

const relationshipSchema: Schema = {
  type: Type.OBJECT,
  properties: {
    relationships: {
      type: Type.ARRAY,
      items: {
        type: Type.OBJECT,
        properties: {
            id: { type: Type.STRING },
            type: { 
                type: Type.STRING, 
                enum: ['EXPANSION', 'CORROBORATION', 'CHALLENGE', 'NUANCE', 'SYNTHESIS', 'PREREQUISITE'],
            },
            reasoning: { type: Type.STRING }
        },
        required: ["id", "type"]
      }
    }
  },
  required: ["relationships"]
};

// --- OPTIMIZATION HEURISTICS ---

// SOTA Optimization: Regex-based Claims Detection.
// We only enable "Grounding" (Search) if the text contains empirical claims.
// This implements "Speculative RAG" - saving massive costs on pure opinion posts.
const EMPIRICAL_MARKERS = [
    /\d+%/, /percent/, /study/, /research/, /data/, /according to/, /cited/, /figure/, 
    /table/, /https?:\/\//, /report/, /analysis shows/, /evidence/, /correlation/, /causation/
];

const requiresGrounding = (text: string): boolean => {
    return EMPIRICAL_MARKERS.some(regex => regex.test(text.toLowerCase()));
};

// --- DQS ALGORITHM IMPLEMENTATION ---

function calculateDQS(data: any, groundingChunks?: any[]): AnalysisResult {
    // 1. Argument Structure Quality (ASQ)
    const t = data.toulmin;
    const c = t.claim ? 1 : 0;
    const g = t.grounds ? 1 : 0;
    const w = t.warrant ? 1 : 0;
    const b = t.backing ? 1 : 0;
    const q = t.qualifier ? 1 : 0;
    const r = t.rebuttal ? 1 : 0;

    const w_g = 1.5; const w_w = 1.0; const w_b = 0.8; const w_q = 0.5; const w_r = 1.2; 

    const ASQ = (c + (g * w_g) + (w * w_w) + (b * w_b) + (q * w_q) + (r * w_r)) / (1 + w_g + w_w + w_b + w_q + w_r);

    // 2. Fallacy Score (FS)
    const FS = Math.max(0, 1 - (data.fallacies.length * 0.15));

    // 3. Cooperative Principle Score (CPS)
    const gr = data.grice;
    const CPS = (gr.quality + gr.quantity + gr.relevance + gr.manner) / 4;

    // 4. Emotional Tone Score (ETS)
    const I = data.sentimentIntensity;
    const ETS = 1 - (I * (1 - ASQ));

    // 5. Final DQS Calculation
    const W_a = 0.35; const W_f = 0.25; const W_c = 0.25; const W_e = 0.15; 
    const DQS_Decimal = (W_a * ASQ) + (W_f * FS) + (W_c * CPS) + (W_e * ETS);
    const score = Math.round(DQS_Decimal * 100);

    // Parse Grounding Sources
    let verifiedSources: { uri: string; title: string }[] = [];
    if (groundingChunks) {
        groundingChunks.forEach((chunk: any) => {
            if (chunk.web && chunk.web.uri) {
                verifiedSources.push({ uri: chunk.web.uri, title: chunk.web.title || new URL(chunk.web.uri).hostname });
            }
        });
    }

    return {
        score,
        scores: {
            ASQ: Math.round(ASQ * 100),
            FS: Math.round(FS * 100),
            CPS: Math.round(CPS * 100),
            ETS: Math.round(ETS * 100)
        },
        toulmin: t,
        fallacies: data.fallacies,
        grice: gr,
        sentimentIntensity: I,
        reasoning: data.reasoning,
        suggestion: data.suggestion,
        tags: data.tags,
        constructive: data.constructive,
        verifiedSources: verifiedSources.length > 0 ? verifiedSources : undefined
    };
}


// --- API FUNCTIONS ---

export const generateEmbedding = async (text: string): Promise<number[] | undefined> => {
  if (!ai || text.length < 15) return undefined; // Skip very short text to save compute
  try {
    const response = await withTimeout<EmbedContentResponse>(ai.models.embedContent({
      model: 'text-embedding-004',
      contents: text
    }), 600000); 
    // Fix: Access embedding via explicit cast or handle types correctly. 
    // Recent SDK types might default to 'embeddings' for batch consistency, but singular returns 'embedding' at runtime.
    return (response as any).embedding?.values || (response as any).embeddings?.[0]?.values;
  } catch (error: any) {
    if (error.message?.includes('429') || error.status === 429) {
        console.warn("Gemini Quota Exceeded (Embeddings). Continuing without vector data.");
        return undefined;
    }
    console.error("Embedding generation error:", error);
    return undefined;
  }
};

export const calculateCosineSimilarity = (vecA: number[], vecB: number[]): number => {
  if (!vecA || !vecB || vecA.length !== vecB.length) return 0;
  const dotProduct = vecA.reduce((acc, val, i) => acc + val * vecB[i], 0);
  const magnitudeA = Math.sqrt(vecA.reduce((acc, val) => acc + val * val, 0));
  const magnitudeB = Math.sqrt(vecB.reduce((acc, val) => acc + val * val, 0));
  if (magnitudeA === 0 || magnitudeB === 0) return 0;
  return dotProduct / (magnitudeA * magnitudeB);
};

export const analyzePostContent = async (text: string, isVideoCaption: boolean = false): Promise<AnalysisResult> => {
  if (!ai) return mockAnalysis();

  try {
    // SOTA Optimization: Speculative RAG
    // Only verify facts if the text actually contains empirical claims.
    const needsGrounding = requiresGrounding(text);
    const tools = needsGrounding ? [{googleSearch: {}}] : [];

    const prompt = `
      Analyze social media post. Output JSON.
      1. Verify claims via Search ONLY if necessary.
      2. Identify Toulmin structure & Fallacies.
      3. Suggest 1 actionable improvement.
      Text: "${text}"
    `;

    const response = await withTimeout<GenerateContentResponse>(ai.models.generateContent({
      model: 'gemini-3-flash-preview', 
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: analysisSchema,
        tools: tools, 
        temperature: 0.1, 
      },
    }), 600000);

    if (!response.text) {
        throw new Error("No text response from Gemini");
    }

    const rawData = JSON.parse(response.text);
    const groundingChunks = response.candidates?.[0]?.groundingMetadata?.groundingChunks;
    
    return calculateDQS(rawData, groundingChunks);

  } catch (error: any) {
    if (error.message?.includes('429') || error.status === 429) {
        console.warn("Gemini Quota Exceeded (Analysis). Switching to Mock Mode.");
        return mockAnalysis();
    }
    console.error("Gemini analysis failed:", error);
    return mockAnalysis();
  }
};

export const analyzeCommentTopics = async (comments: {id: string, content: string}[]): Promise<Record<string, string>> => {
  if (!ai || comments.length === 0) {
      const map: Record<string, string> = {};
      comments.forEach(c => map[c.id] = "General");
      return map;
  }
  try {
    const prompt = `Label topics (1-2 words) for IDs: ${JSON.stringify(comments.map(c => ({id: c.id, content: c.content})))}`;
    const response = await withTimeout<GenerateContentResponse>(ai.models.generateContent({
      model: 'gemini-3-flash-preview',
      contents: prompt,
      config: { responseMimeType: "application/json", responseSchema: commentTopicsSchema },
    }));
    
    if (!response.text) return {};
    const result = JSON.parse(response.text);
    const map: Record<string, string> = {};
    if (result.mappings) result.mappings.forEach((m: any) => { map[m.id] = m.topic; });
    return map;
  } catch (error) {
    return {};
  }
};

export const analyzePostTopic = async (content: string, existingTopics: string[]): Promise<string> => {
    return analyzeSingleCommentTopic(content, existingTopics);
}

export const analyzeSingleCommentTopic = async (content: string, existingTopics: string[]): Promise<string> => {
    if (!ai) return "General";
    try {
        const prompt = `Classify content: "${content}". Options: ${existingTopics.join(", ")} or New.`;
        const response = await withTimeout<GenerateContentResponse>(ai.models.generateContent({
          model: 'gemini-3-flash-preview',
          contents: prompt,
          config: { responseMimeType: "application/json", responseSchema: singleTopicSchema },
        }));
        if (!response.text) return "General";
        return JSON.parse(response.text).topic;
      } catch (error) {
        return "General";
      }
}

// SOTA Optimization: Semantic Gating for Knowledge Graphs
// Instead of expensive LLM calls for every pair, we use vector heuristics for the extremes.
export const analyzePostRelationships = async (
    sourceContent: string, 
    targets: {id: string, content: string, similarity?: number}[]
): Promise<Record<string, SemanticRelationship>> => {
    
    if (!ai) {
        console.warn("[AI] Missing API Key.");
        return {};
    }
    if (targets.length === 0) return {};
    
    const map: Record<string, SemanticRelationship> = {};
    const candidatesForLLM: typeof targets = [];

    // --- STEP 1: SEMANTIC GATING (Heuristic Layer) ---
    // Save tokens by auto-classifying obvious vector relationships
    targets.forEach(t => {
        // If similarity is extremely high (>0.92), it's almost certainly Corroboration or Restatement.
        if (t.similarity && t.similarity > 0.92) {
            console.log(`[AI] Auto-mapped ${t.id} -> CORROBORATION (Similarity: ${t.similarity})`);
            map[t.id] = 'CORROBORATION';
        }
        // If similarity is too low (<0.65), it's likely noise in the "Related" search. Ignore it.
        // We only want to spend compute on the "Goldilocks Zone" (0.65 - 0.92) where nuance lives.
        else if (t.similarity && t.similarity < 0.65) {
             console.log(`[AI] Dropped ${t.id} (Similarity too low: ${t.similarity})`);
             // Do nothing, don't map.
        } 
        else {
            candidatesForLLM.push(t);
        }
    });

    if (candidatesForLLM.length === 0) {
        return map;
    }

    // --- STEP 2: LLM REASONING (The "Goldilocks Zone") ---
    try {
        console.log(`[AI] Deep Analyzing ${candidatesForLLM.length} candidates in the Goldilocks Zone...`);

        const prompt = `
            Task: Classify rhetorical relationship of Targets relative to Source.
            Source: "${sourceContent.substring(0, 400)}..."
            Targets: ${JSON.stringify(candidatesForLLM.map(t => ({id: t.id, content: t.content.substring(0, 200)})))}
            
            Types:
            1. EXPANSION (Broadens scope)
            2. CORROBORATION (Supports claim)
            3. CHALLENGE (Disagrees)
            4. NUANCE (Adds conditions)
            5. SYNTHESIS (Combines ideas)
            6. PREREQUISITE (Foundational)
        `;

        const response = await withTimeout<GenerateContentResponse>(ai.models.generateContent({
            model: 'gemini-3-flash-preview',
            contents: prompt,
            config: { 
                responseMimeType: "application/json", 
                responseSchema: relationshipSchema,
                temperature: 0.0
            }
        }), 600000);

        if (!response.text) return map;
        const result = JSON.parse(response.text);
        
        if (result.relationships) {
            result.relationships.forEach((r: any) => { 
                map[r.id] = r.type; 
            });
        }
        return map;

    } catch (e: any) {
        console.error("Relationship Analysis Failed", e);
        return map; // Return whatever we heuristic-mapped
    }
}

const mockAnalysis = (): AnalysisResult => ({
  score: 50,
  scores: { ASQ: 50, FS: 100, CPS: 50, ETS: 50 },
  toulmin: { claim: true, grounds: false, warrant: false, backing: false, qualifier: false, rebuttal: false },
  fallacies: [],
  grice: { quality: 0.5, quantity: 0.5, relevance: 0.5, manner: 0.5 },
  sentimentIntensity: 0.2,
  reasoning: "AI Analysis unavailable (Quota Exceeded - Mock Mode).",
  suggestion: "Try adding more evidence to support your claims.",
  tags: ["Unverified", "SystemLimit"],
  constructive: true
});
