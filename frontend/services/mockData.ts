
import { Post, PostType } from '../types';

const BASE_ANALYSIS = {
    toulmin: { claim: true, grounds: true, warrant: true, backing: true, qualifier: true, rebuttal: false },
    fallacies: [],
    grice: { quality: 0.9, quantity: 0.9, relevance: 1.0, manner: 0.9 },
    sentimentIntensity: 0.1,
    scores: { ASQ: 90, FS: 100, CPS: 90, ETS: 95 },
    suggestion: "Consider adding a rebuttal to address common counter-arguments."
};

const MOCK_SUB_COMMENTS: Post[] = [
    {
        id: 'c-1-sub1',
        parentId: 'c-1',
        author: { id: 'u11', name: 'CuriousStudent', handle: 'student_x', avatar: 'https://picsum.photos/id/111/50/50', reputationScore: 60 },
        content: "Could you elaborate on the stress variable? Is it acute or chronic?",
        type: PostType.TEXT,
        timestamp: new Date(Date.now() - 1000 * 60 * 28),
        analysis: {
            ...BASE_ANALYSIS,
            score: 75,
            reasoning: "Good clarifying question.",
            tags: ["Question", "Clarification"],
            constructive: true,
            suggestion: "No changes needed, clear and concise."
        },
        topic: "Methodology",
        comments: [],
        likes: 2,
        bookmarks: 0
    },
     {
        id: 'c-1-sub2',
        parentId: 'c-1',
        author: { id: 'u12', name: 'OriginalPoster', handle: 'op_user', avatar: 'https://picsum.photos/id/112/50/50', reputationScore: 70 },
        content: "I believe the study mostly looked at chronic stress markers like baseline cortisol.",
        type: PostType.TEXT,
        timestamp: new Date(Date.now() - 1000 * 60 * 20),
        analysis: {
            ...BASE_ANALYSIS,
            score: 80,
            reasoning: "Helpful answer providing context.",
            tags: ["Answer", "Context"],
            constructive: true,
            suggestion: "Linking to the specific figure in the study would strengthen this."
        },
        topic: "Methodology",
        comments: [],
        likes: 5,
        bookmarks: 0
    }
];

const MOCK_COMMENTS_1: Post[] = [
  {
    id: 'c-1',
    parentId: 'p-1',
    author: { id: 'u4', name: 'LogicFan', handle: 'logic_101', avatar: 'https://picsum.photos/id/55/50/50', reputationScore: 80 },
    content: "This is a great point. I hadn't considered the variable of stress on receptor density.",
    type: PostType.TEXT,
    timestamp: new Date(Date.now() - 1000 * 60 * 30),
    analysis: {
        ...BASE_ANALYSIS,
        score: 85,
        reasoning: "Acknowledges a valid point and reflects on new information.",
        tags: ["Constructive", "Reflection"],
        constructive: true,
        suggestion: "You could expand on why this variable changes your perspective."
    },
    topic: "Methodology",
    comments: MOCK_SUB_COMMENTS,
    likes: 5,
    bookmarks: 0
  },
  {
    id: 'c-3',
    parentId: 'p-1',
    author: { id: 'u6', name: 'NeuroDoc', handle: 'brain_md', avatar: 'https://picsum.photos/id/77/50/50', reputationScore: 95 },
    content: "Actually, looking at the supplemental data (Figure S3), they did attempt to control for cortisol levels, which is a proxy for stress.",
    type: PostType.TEXT,
    timestamp: new Date(Date.now() - 1000 * 60 * 25),
    analysis: {
        ...BASE_ANALYSIS,
        score: 92,
        reasoning: "Provides specific evidence from the source to clarify the discussion.",
        tags: ["Evidence-Based", "Clarification"],
        constructive: true,
        suggestion: "Excellent use of evidence."
    },
    topic: "Evidence",
    comments: [],
    likes: 12,
    bookmarks: 0
  }
];

const MOCK_COMMENTS_2: Post[] = [
    {
        id: 'c-6',
        parentId: 'p-2',
        author: { id: 'u9', name: 'CarLover', handle: 'v8_engine', avatar: 'https://picsum.photos/id/101/50/50', reputationScore: 50 },
        content: "But what about freedom? I want to drive my car where I want.",
        type: PostType.TEXT,
        timestamp: new Date(Date.now() - 1000 * 60 * 120),
        analysis: {
            ...BASE_ANALYSIS,
            score: 60,
            scores: { ASQ: 40, FS: 90, CPS: 50, ETS: 50 },
            toulmin: { ...BASE_ANALYSIS.toulmin, grounds: false, warrant: false },
            reasoning: "Valid personal value but lacks engagement with the economic data presented.",
            tags: ["Values", "Emotional"],
            constructive: true,
            suggestion: "Acknowledge the economic data before pivoting to personal values to strengthen the argument."
        },
        topic: "Freedom",
        comments: [],
        likes: 3,
        bookmarks: 0
    }
];

// Hidden post that serves as a semantic link
export const LINKED_POST_4: Post = {
    id: 'p-4',
    author: {
        id: 'u13',
        name: 'HealthMetrics',
        handle: 'stat_health',
        avatar: 'https://picsum.photos/id/200/100/100',
        reputationScore: 88
    },
    content: "Meta-analysis of 50 studies confirms: Environmental stressors (noise, pollution) elevate baseline cortisol by 15% on average, significantly altering neurotransmitter sensitivity.",
    type: PostType.TEXT,
    topic: "Neuroscience",
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24),
    analysis: {
        ...BASE_ANALYSIS,
        score: 91,
        reasoning: "High quality data synthesis relevant to biochemical discussions.",
        tags: ["Data", "Cortisol", "Environment"],
        constructive: true,
        suggestion: "No improvements needed.",
        verifiedSources: [{ uri: "https://pubmed.ncbi.nlm.nih.gov", title: "PubMed Meta-Analysis" }],
        semanticConnections: [
            { postId: 'p-1', type: 'CORROBORATION' }, // Supports p-1's claim about stress
            { postId: 'p-5', type: 'CORROBORATION' }  // Supports p-5's claim about noise
        ]
    },
    likes: 150,
    bookmarks: 45,
    comments: [],
    relatedPostIds: []
}

export const INITIAL_POSTS: Post[] = [
  {
    id: 'p-1',
    author: {
      id: 'u1',
      name: 'Dr. Sarah Chen',
      handle: 'schen_neuro',
      avatar: 'https://picsum.photos/id/64/100/100',
      reputationScore: 92
    },
    content: "The recent study on dopamine fasting lacks a control group for socio-economic stress factors. While the methodology is sound regarding receptor density, we can't ignore environmental variables. Correlation is not causation.",
    type: PostType.TEXT,
    topic: "Neuroscience",
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2),
    analysis: {
      ...BASE_ANALYSIS,
      score: 94,
      reasoning: "Excellent identification of methodological limitations without dismissing the study entirely.",
      tags: ["Scientific Method", "Nuance", "Critical Thinking"],
      constructive: true,
      suggestion: "Perfect. No suggestions.",
      verifiedSources: [{ uri: "https://nature.com/articles/dopamine", title: "Nature Neuroscience" }],
      semanticConnections: [
          { postId: 'p-4', type: 'CORROBORATION' }, // p-4 provides data backing this
          { postId: 'p-5', type: 'SYNTHESIS' }      // Connects to Urbanism/Noise
      ]
    },
    likes: 45,
    bookmarks: 12,
    comments: MOCK_COMMENTS_1,
    relatedPostIds: []
  },
  {
    id: 'p-2',
    author: {
      id: 'u2',
      name: 'Urbanist Daily',
      handle: 'urban_planning',
      avatar: 'https://picsum.photos/id/122/100/100',
      reputationScore: 88
    },
    content: "Why walkable cities generate more economic value per acre than sprawling suburbs. A breakdown of tax revenue vs infrastructure maintenance costs.",
    type: PostType.VIDEO,
    topic: "Urbanism",
    thumbnailUrl: 'https://picsum.photos/id/188/400/700',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 5),
    analysis: {
      ...BASE_ANALYSIS,
      score: 85,
      reasoning: "Clear economic argument supported by data concepts.",
      tags: ["Economics", "Urbanism", "Data-Driven"],
      constructive: true,
      suggestion: "Cite a specific case study (e.g. Strong Towns) to boost the Grounds score.",
      semanticConnections: [
          { postId: 'p-5', type: 'EXPANSION' } // p-5 adds the "Sound" dimension to this topic
      ]
    },
    likes: 120,
    bookmarks: 89,
    comments: MOCK_COMMENTS_2,
    relatedPostIds: []
  },
  {
    id: 'p-3',
    author: {
      id: 'u3',
      name: 'Tech Skeptic',
      handle: 'tech_realist',
      avatar: 'https://picsum.photos/id/237/100/100',
      reputationScore: 45
    },
    content: "Crypto is largely a speculative bubble that produces more carbon waste than utility. Most tokens are just gambling mechanisms for digital-native enthusiasts.",
    type: PostType.TEXT,
    topic: "Finance",
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 8),
    analysis: {
      ...BASE_ANALYSIS,
      score: 40,
      scores: { ASQ: 45, FS: 90, CPS: 50, ETS: 40 },
      toulmin: { ...BASE_ANALYSIS.toulmin, grounds: false, backing: false },
      reasoning: "Presents a common critique but lacks deep analysis of the underlying tech or market shifts.",
      tags: ["Skepticism", "Environment", "Finance"],
      constructive: true,
      suggestion: "You are missing Grounds (evidence). Reference energy consumption reports (e.g., Cambridge Index) to support your carbon claim.",
      semanticConnections: [
          { postId: 'p-6', type: 'CHALLENGE' } // p-6 challenges the "pure speculation" view with "regulation"
      ]
    },
    likes: 12,
    bookmarks: 0,
    comments: [],
    relatedPostIds: []
  },
  LINKED_POST_4,
  {
    id: 'p-5',
    author: {
      id: 'u14',
      name: 'AcousticEcology',
      handle: 'sound_scape',
      avatar: 'https://picsum.photos/id/201/100/100',
      reputationScore: 82
    },
    content: "The impact of noise pollution on cognitive function in urban residents is often overlooked. Soundscape design is just as critical as zoning for long-term community health and reducing stress response.",
    type: PostType.TEXT,
    topic: "Urbanism",
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 12),
    analysis: {
      ...BASE_ANALYSIS,
      score: 88,
      reasoning: "Solid cross-disciplinary analysis linking urbanism and biology.",
      tags: ["Public Health", "Acoustics", "Urban Design"],
      constructive: true,
      suggestion: "Consider quantifying 'impact' with a stat to improve Precision.",
      semanticConnections: [
          { postId: 'p-2', type: 'EXPANSION' },    // Expands on Urbanism
          { postId: 'p-1', type: 'SYNTHESIS' },    // Connects Urbanism to Neuro (Stress)
          { postId: 'p-4', type: 'CORROBORATION' } // Uses p-4 as evidence
      ]
    },
    likes: 32,
    bookmarks: 14,
    comments: [],
    relatedPostIds: []
  },
  {
    id: 'p-6',
    author: {
      id: 'u15',
      name: 'FinTech Analyst',
      handle: 'fin_guard',
      avatar: 'https://picsum.photos/id/202/100/100',
      reputationScore: 90
    },
    content: "While decentralization is a key tenet of blockchain, the volatility of the crypto market suggests a need for institutional guardrails or stablecoin regulation to prevent systemic risks.",
    type: PostType.TEXT,
    topic: "Finance",
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 18),
    analysis: {
      ...BASE_ANALYSIS,
      score: 75,
      reasoning: "Balanced view considering both tech and economic stability.",
      tags: ["Regulation", "Crypto", "Finance"],
      constructive: true,
      suggestion: "What specific regulation model do you propose? Adding a Warrant here would improve the structure.",
      semanticConnections: [
          { postId: 'p-3', type: 'NUANCE' } // Adds nuance to p-3's blunt critique
      ]
    },
    likes: 22,
    bookmarks: 5,
    comments: [],
    relatedPostIds: []
  }
];
