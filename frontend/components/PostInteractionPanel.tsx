
import React, { useState, useEffect, useMemo } from 'react';
import { Post, SemanticRelationship } from '../types';
import { PostCard } from './PostCard';
import { backend } from '../services/backend';
import { analyzeCommentTopics, analyzeSingleCommentTopic } from '../services/geminiService';
import { Layers, Link as LinkIcon, Sparkles, Filter, Loader2, Send, GitMerge, CheckCircle2, Split, BookOpen, Scaling, GitCompare, LayoutGrid, Hash, Tag } from 'lucide-react';

interface PostInteractionPanelProps {
  post: Post;
  onCommentClick: (comment: Post) => void;
  isFeedMode?: boolean; 
}

type TabView = 'DISCOURSE' | 'LINKS';

interface LinkFilter {
    id: string;
    label: string;
    type: SemanticRelationship;
    count: number;
}

interface TopicFilter {
    id: string;
    count: number;
}

export const PostInteractionPanel: React.FC<PostInteractionPanelProps> = ({ post, onCommentClick, isFeedMode = false }) => {
  const [comments, setComments] = useState<Post[]>(post.comments || []);
  const [newComment, setNewComment] = useState('');
  const [activeTab, setActiveTab] = useState<TabView>('DISCOURSE');
  
  const [linkedPosts, setLinkedPosts] = useState<{post: Post, score: number, relationship?: SemanticRelationship}[]>([]);
  const [isLoadingLinks, setIsLoadingLinks] = useState(false);
  const [hasFetchedLinks, setHasFetchedLinks] = useState(false);
  
  // --- FILTER STATE ---
  const [activeLinkFilter, setActiveLinkFilter] = useState<string>('All');
  const [activeLinkTopic, setActiveLinkTopic] = useState<string>('All');

  const [topics, setTopics] = useState<string[]>(() => {
    const currentComments = post.comments || [];
    const uniqueTopics = Array.from(new Set(currentComments.map(c => c.topic || 'General')));
    return ['All', ...uniqueTopics.sort()];
  });
  const [selectedTopic, setSelectedTopic] = useState<string>('All');
  const [isProcessingNewComment, setIsProcessingNewComment] = useState(false);

  // Fetch Links when Tab changes
  useEffect(() => {
    if (activeTab === 'LINKS' && !hasFetchedLinks) {
        setIsLoadingLinks(true);
        backend.getRelatedPosts(post.id, 'DISCOVERY')
            .then((data) => {
                setLinkedPosts(data);
                setHasFetchedLinks(true);
            })
            .catch(e => console.error(e))
            .finally(() => setIsLoadingLinks(false));
    }
  }, [activeTab, post.id, hasFetchedLinks]);

  // --- DYNAMIC FILTERS (Multi-Axis) ---
  const linkTopics = useMemo(() => {
      const pool = activeLinkFilter === 'All' 
          ? linkedPosts 
          : linkedPosts.filter(l => l.relationship === activeLinkFilter);
      
      const counts: Record<string, number> = {};
      pool.forEach(p => {
          const t = p.post.topic || 'General';
          counts[t] = (counts[t] || 0) + 1;
      });

      return [
          { id: 'All', count: pool.length },
          ...Object.entries(counts)
            .map(([topic, count]) => ({ id: topic, count }))
            .sort((a, b) => b.count - a.count)
      ];
  }, [linkedPosts, activeLinkFilter]);

  const linkFilters = useMemo(() => {
      const pool = activeLinkTopic === 'All' 
          ? linkedPosts 
          : linkedPosts.filter(l => (l.post.topic || 'General') === activeLinkTopic);

      const counts: Record<string, number> = {};
      pool.forEach(p => {
          const r = p.relationship || 'UNCATEGORIZED';
          counts[r] = (counts[r] || 0) + 1;
      });
      
      return [
        { id: 'All', label: 'All', type: 'UNCATEGORIZED', count: pool.length } as LinkFilter,
        ...Object.entries(counts).map(([type, count]) => {
             if (type === 'UNCATEGORIZED') return null;
             return {
                 id: type,
                 label: type.charAt(0) + type.slice(1).toLowerCase(),
                 type: type as SemanticRelationship,
                 count
             };
        }).filter(Boolean) as LinkFilter[]
      ];
  }, [linkedPosts, activeLinkTopic]);

  useEffect(() => {
      if (activeLinkTopic !== 'All' && !linkTopics.some(t => t.id === activeLinkTopic)) {
          setActiveLinkTopic('All');
      }
  }, [linkTopics, activeLinkTopic]);

  useEffect(() => {
      if (activeLinkFilter !== 'All' && !linkFilters.some(f => f.id === activeLinkFilter)) {
          setActiveLinkFilter('All');
      }
  }, [linkFilters, activeLinkFilter]);

  // Analyze topics for comments if missing
  useEffect(() => {
    const currentComments = comments;
    const needsAnalysis = currentComments.length > 0 && currentComments.some(c => !c.topic);

    if (needsAnalysis) {
        analyzeCommentTopics(currentComments.map(c => ({id: c.id, content: c.content})))
            .then(mapping => {
                const updatedComments = currentComments.map(c => ({
                    ...c,
                    topic: mapping[c.id] || 'General'
                }));
                setComments(updatedComments);
                updateTopicsList(updatedComments);
            })
            .catch(err => {
                console.error(err);
                updateTopicsList(currentComments);
            });
    }
  }, [post.id]);

  const updateTopicsList = (currentComments: Post[]) => {
      const uniqueTopics = Array.from(new Set(currentComments.map(c => c.topic || 'General')));
      setTopics(['All', ...uniqueTopics.sort()]);
  };

  const handlePostComment = async () => {
    if (!newComment.trim()) return;
    setIsProcessingNewComment(true);
    try {
        const addedComment = await backend.createComment(post.id, newComment);
        const newTopic = await analyzeSingleCommentTopic(addedComment.content, topics);
        addedComment.topic = newTopic; 
        
        setComments(prev => [addedComment, ...prev]);
        setNewComment('');
        updateTopicsList([addedComment, ...comments]);
    } catch (e) {
        console.error("Failed to post comment", e);
    } finally {
        setIsProcessingNewComment(false);
    }
  };

  const filteredComments = selectedTopic === 'All' ? comments : comments.filter(c => c.topic === selectedTopic);
  
  const filteredLinks = linkedPosts.filter(l => {
      const matchRel = activeLinkFilter === 'All' || l.relationship === activeLinkFilter;
      const matchTopic = activeLinkTopic === 'All' || (l.post.topic || 'General') === activeLinkTopic;
      return matchRel && matchTopic;
  });

  return (
    <div className="flex flex-col h-full bg-slate-900 relative">
        {/* Tabs Header - Reduced padding for Mobile */}
        <div className="px-4 border-b border-slate-800 bg-slate-900/95 backdrop-blur sticky top-0 z-20 flex items-center gap-6 justify-between shrink-0">
            <div className="flex items-center gap-6 w-full">
                <button onClick={() => setActiveTab('DISCOURSE')} className={`py-3 md:py-4 text-xs md:text-sm font-semibold flex items-center justify-center flex-1 gap-2 border-b-2 transition-colors ${activeTab === 'DISCOURSE' ? 'text-white border-primary-500' : 'text-slate-500 border-transparent hover:text-slate-300'}`}>
                    <Layers size={14} /> Discourse
                </button>
                <button onClick={() => setActiveTab('LINKS')} className={`py-3 md:py-4 text-xs md:text-sm font-semibold flex items-center justify-center flex-1 gap-2 border-b-2 transition-colors ${activeTab === 'LINKS' ? 'text-white border-emerald-500' : 'text-slate-500 border-transparent hover:text-slate-300'}`}>
                    <LinkIcon size={14} /> Graph 
                    {linkedPosts.length > 0 && (
                        <span className="text-[10px] bg-slate-800 px-1.5 py-0.5 rounded-full">{linkedPosts.length}</span>
                    )}
                </button>
            </div>
        </div>
        
        {/* Scrollable Content Area */}
        <div 
            className="flex-1 overflow-y-auto scrollbar-thin bg-slate-950 relative min-h-0 z-0 overscroll-contain pb-2"
            onWheel={(e) => e.stopPropagation()} 
        >
            {activeTab === 'DISCOURSE' && (
                <div className="flex flex-col">
                    {comments.length > 0 && (
                        <div className="sticky top-0 z-10 px-4 py-2 border-b border-slate-800 bg-slate-900/95 backdrop-blur flex gap-2 overflow-x-auto no-scrollbar shrink-0 shadow-sm touch-action-pan-x">
                            {topics.map(topic => (
                                <button key={topic} onClick={() => setSelectedTopic(topic)} className={`px-2 py-1 rounded-full text-[10px] font-medium transition-all whitespace-nowrap border ${selectedTopic === topic ? 'bg-primary-600 border-primary-500 text-white' : 'bg-slate-800 border-slate-700 text-slate-400 hover:bg-slate-700'}`}>
                                    {topic}
                                </button>
                            ))}
                        </div>
                    )}
                    <div className="p-4 space-y-4">
                        {filteredComments.length > 0 ? (
                            filteredComments.map(comment => (
                                <PostCard key={comment.id} post={comment} onClick={() => onCommentClick(comment)} />
                            ))
                        ) : (
                            <div className="text-center py-10 text-slate-500 text-sm italic">
                                No discourse yet.
                            </div>
                        )}
                    </div>
                </div>
            )}

            {activeTab === 'LINKS' && (
                <div className="flex flex-col min-h-full">
                    
                    {/* MULTI-AXIS FILTER HEADER - Optimized for Horizontal Touch Scroll */}
                    <div className="sticky top-0 z-10 bg-slate-900/95 backdrop-blur border-b border-slate-800 shadow-lg">
                        
                        {/* Axis 1: Topics (Context) */}
                        {linkTopics.length > 0 && (
                             <div className="px-4 py-2 flex gap-2 overflow-x-auto no-scrollbar border-b border-slate-800/50 touch-action-pan-x">
                                <div className="flex items-center mr-1 text-slate-500 shrink-0">
                                    <Hash size={12} />
                                </div>
                                {linkTopics.map(filter => (
                                    <button 
                                        key={filter.id}
                                        onClick={() => setActiveLinkTopic(filter.id)}
                                        className={`px-2.5 py-1 rounded-md text-[10px] font-medium whitespace-nowrap border flex items-center gap-1.5 transition-all shrink-0 ${
                                            activeLinkTopic === filter.id 
                                            ? 'bg-slate-100 text-slate-900 border-white' 
                                            : 'bg-slate-800 border-slate-700 text-slate-400 hover:bg-slate-700'
                                        }`}
                                    >
                                        {filter.id}
                                        <span className={`text-[9px] px-1 rounded-full ${activeLinkTopic === filter.id ? 'bg-slate-300 text-slate-800' : 'bg-slate-900 text-slate-500'}`}>
                                            {filter.count}
                                        </span>
                                    </button>
                                ))}
                             </div>
                        )}

                        {/* Axis 2: Semantic Relationship (Rhetoric) */}
                        {linkFilters.length > 0 && (
                             <div className="px-4 py-2 flex gap-2 overflow-x-auto no-scrollbar touch-action-pan-x">
                                <div className="flex items-center mr-1 text-slate-500 shrink-0">
                                    <GitMerge size={12} className="rotate-90" />
                                </div>
                                {linkFilters.map(filter => {
                                    const isActive = activeLinkFilter === filter.id;
                                    let Icon = LayoutGrid;
                                    let colorClass = isActive ? "bg-slate-700 border-slate-500 text-white shadow-sm" : "bg-slate-800/50 border-slate-800 text-slate-500 grayscale opacity-70 hover:opacity-100 hover:grayscale-0";
                                    
                                    if (isActive) {
                                        if (filter.type === 'PREREQUISITE') colorClass = "bg-slate-600 border-slate-400 text-white";
                                        else if (filter.type === 'EXPANSION') colorClass = "bg-sky-700 border-sky-500 text-white";
                                        else if (filter.type === 'CORROBORATION') colorClass = "bg-emerald-700 border-emerald-500 text-white";
                                        else if (filter.type === 'CHALLENGE') colorClass = "bg-rose-700 border-rose-500 text-white";
                                        else if (filter.type === 'NUANCE') colorClass = "bg-indigo-700 border-indigo-500 text-white";
                                        else if (filter.type === 'SYNTHESIS') colorClass = "bg-fuchsia-700 border-fuchsia-500 text-white";
                                    } 

                                    // Icons
                                    if (filter.type === 'PREREQUISITE') Icon = BookOpen;
                                    else if (filter.type === 'EXPANSION') Icon = Scaling;
                                    else if (filter.type === 'CORROBORATION') Icon = CheckCircle2;
                                    else if (filter.type === 'CHALLENGE') Icon = GitCompare;
                                    else if (filter.type === 'NUANCE') Icon = Split;
                                    else if (filter.type === 'SYNTHESIS') Icon = GitMerge;

                                    return (
                                        <button 
                                            key={filter.id} 
                                            onClick={() => setActiveLinkFilter(filter.id)} 
                                            className={`px-2.5 py-1 rounded-full text-[10px] font-bold transition-all whitespace-nowrap border flex items-center gap-1.5 shrink-0 ${colorClass}`}
                                        >
                                            <Icon size={12} />
                                            <span>{filter.label}</span>
                                        </button>
                                    );
                                })}
                            </div>
                        )}
                    </div>

                    <div className="p-4 space-y-3 flex-1">
                        {isLoadingLinks ? (
                            <div className="flex justify-center items-center py-10">
                                <Loader2 className="animate-spin text-emerald-500" size={32} />
                            </div>
                        ) : filteredLinks.length > 0 ? (
                            <>
                                <div className="mb-2 px-1 flex justify-between items-center">
                                    <h4 className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                                        <Sparkles size={10} className="text-emerald-500" /> 
                                        Filtered Graph Nodes ({filteredLinks.length})
                                    </h4>
                                </div>
                                {filteredLinks.map((item) => (
                                    <LinkedPostItem 
                                        key={item.post.id} 
                                        post={item.post} 
                                        score={item.score}
                                        relationship={item.relationship}
                                        onClick={() => onCommentClick(item.post)} 
                                    />
                                ))}
                            </>
                        ) : (
                            <div className="flex flex-col items-center justify-center py-20 text-slate-500">
                                <Filter size={32} className="mb-3 opacity-20" />
                                <p className="text-sm">No connections match this combination.</p>
                                <button 
                                    onClick={() => { setActiveLinkFilter('All'); setActiveLinkTopic('All'); }}
                                    className="mt-4 text-xs text-primary-400 hover:text-primary-300 underline"
                                >
                                    Clear Filters
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>

        {/* Fixed Input Area (Outside Scroll) - Only for Discourse - Safe Area handling */}
        {activeTab === 'DISCOURSE' && (
            <div className="p-3 border-t border-slate-800 bg-slate-900/95 backdrop-blur shrink-0 z-20 pb-safe">
                <div className="flex gap-3">
                    <div className="flex-1">
                        <div className="relative">
                            <input
                                value={newComment}
                                onChange={(e) => setNewComment(e.target.value)}
                                placeholder="Add to the discourse..."
                                className="w-full bg-slate-950 border border-slate-800 rounded-full px-4 py-3 pr-24 text-sm text-slate-200 focus:outline-none focus:border-primary-500"
                                disabled={isProcessingNewComment}
                                onKeyDown={(e) => e.key === 'Enter' && handlePostComment()}
                            />
                            <div className="absolute right-1 top-1 bottom-1 flex items-center">
                                <button
                                    onClick={handlePostComment}
                                    disabled={!newComment.trim() || isProcessingNewComment}
                                    className={`h-full aspect-square rounded-full flex items-center justify-center transition-colors ${
                                        !newComment.trim() || isProcessingNewComment
                                        ? 'bg-slate-800 text-slate-600'
                                        : 'bg-primary-600 hover:bg-primary-500 text-white'
                                    }`}
                                >
                                    {isProcessingNewComment ? <Loader2 size={14} className="animate-spin" /> : <Send size={14} />}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        )}
    </div>
  );
};

const LinkedPostItem: React.FC<{ post: Post; score: number; relationship?: SemanticRelationship; onClick: () => void }> = ({ post, score, relationship, onClick }) => {
    const percent = Math.round(score * 100);
    
    let relBadge = null;
    if (relationship && relationship !== 'UNCATEGORIZED') {
        if (relationship === 'PREREQUISITE') relBadge = <span className="text-[8px] bg-slate-700/50 text-slate-300 border border-slate-600 px-1.5 py-0.5 rounded uppercase flex items-center gap-1 font-bold tracking-wide"><BookOpen size={8} /> Prerequisite</span>;
        else if (relationship === 'EXPANSION') relBadge = <span className="text-[8px] bg-sky-900/30 text-sky-400 border border-sky-900/50 px-1.5 py-0.5 rounded uppercase flex items-center gap-1 font-bold tracking-wide"><Scaling size={8} /> Expansion</span>;
        else if (relationship === 'CORROBORATION') relBadge = <span className="text-[8px] bg-emerald-900/30 text-emerald-400 border border-emerald-900/50 px-1.5 py-0.5 rounded uppercase flex items-center gap-1 font-bold tracking-wide"><CheckCircle2 size={8} /> Corroboration</span>;
        else if (relationship === 'CHALLENGE') relBadge = <span className="text-[8px] bg-rose-900/30 text-rose-400 border border-rose-900/50 px-1.5 py-0.5 rounded uppercase flex items-center gap-1 font-bold tracking-wide"><GitCompare size={8} /> Challenge</span>;
        else if (relationship === 'NUANCE') relBadge = <span className="text-[8px] bg-indigo-900/30 text-indigo-400 border border-indigo-900/50 px-1.5 py-0.5 rounded uppercase flex items-center gap-1 font-bold tracking-wide"><Split size={8} /> Nuance</span>;
        else if (relationship === 'SYNTHESIS') relBadge = <span className="text-[8px] bg-fuchsia-900/30 text-fuchsia-400 border border-fuchsia-900/50 px-1.5 py-0.5 rounded uppercase flex items-center gap-1 font-bold tracking-wide"><GitMerge size={8} /> Synthesis</span>;
    }

    return (
        <div onClick={onClick} className="bg-slate-800/30 border border-slate-700/50 hover:bg-slate-800/60 hover:border-emerald-500/30 rounded-lg p-3 cursor-pointer transition-all group flex gap-3">
            {/* Score Visualization */}
            <div className="flex flex-col gap-1 shrink-0 w-12 justify-center">
                 <div className="text-[9px] text-emerald-400 font-bold text-center">{percent}%</div>
                 <div className="w-full h-1 bg-slate-700 rounded-full overflow-hidden">
                    <div className="h-full rounded-full bg-emerald-500" style={{ width: `${percent}%` }}></div>
                 </div>
            </div>
            
            <div className="flex-1 min-w-0 border-l border-slate-800 pl-3">
                <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                    <h5 className="text-xs font-semibold text-slate-300 truncate mr-auto">
                        {post.author.name} 
                    </h5>
                    {post.topic && (
                        <span className="text-[8px] bg-slate-900 text-slate-400 border border-slate-700 px-1.5 py-0.5 rounded uppercase font-bold tracking-wide">
                            {post.topic}
                        </span>
                    )}
                    {relBadge}
                </div>
                <p className="text-xs text-slate-400 line-clamp-2 italic">"{post.content}"</p>
            </div>
        </div>
    );
};
