
import React, { useState } from 'react';
import { Post, PostType } from '../types';
import { PostInteractionPanel } from './PostInteractionPanel';
import { AnalysisBadge } from './AnalysisBadge';
import { PostCard } from './PostCard'; 
import { Play, MoreHorizontal, Bookmark, Share2 } from 'lucide-react';

interface FeedSlideProps {
    post: Post;
    onCommentClick: (comment: Post) => void;
}

export const FeedSlide: React.FC<FeedSlideProps> = ({ post, onCommentClick }) => {
    const [showFullAnalysis, setShowFullAnalysis] = useState(false);

    return (
        // Height is managed by parent container for 100dvh minus padding
        <div className="w-full h-full snap-start shrink-0 flex flex-col bg-slate-950 overflow-hidden relative border-b border-slate-900">
            
            {/* TOP HALF: Post Content (50% height for mobile balance) */}
            <div className="h-[50%] md:h-[55%] relative flex flex-col shrink-0">
                
                {/* VIDEO LAYOUT (Immersive Custom Layout) */}
                {post.type === PostType.VIDEO ? (
                    <div className="h-full w-full bg-black relative flex flex-col">
                         {/* Header Overlay */}
                        <div className="absolute top-0 left-0 right-0 p-4 z-20 flex justify-between items-start bg-gradient-to-b from-black/80 to-transparent pointer-events-none">
                            <div className="flex gap-3 pointer-events-auto">
                                <img 
                                    src={post.author.avatar} 
                                    alt={post.author.name} 
                                    className="w-10 h-10 rounded-full border border-slate-600 shadow-md"
                                />
                                <div className="flex flex-col text-shadow-sm">
                                    <span className="font-bold text-white text-sm">{post.author.name}</span>
                                    <span className="text-xs text-slate-300">@{post.author.handle}</span>
                                </div>
                            </div>
                            <button className="text-white p-2 bg-black/20 rounded-full backdrop-blur-sm hover:bg-black/40 pointer-events-auto">
                                <MoreHorizontal size={20} />
                            </button>
                        </div>

                        {/* Video Content */}
                        <div className="flex-1 relative flex items-center justify-center overflow-hidden bg-slate-900">
                             <img 
                                src={post.thumbnailUrl} 
                                className="w-full h-full object-cover opacity-80" 
                                alt="Video BG"
                             />
                             <div className="absolute inset-0 flex items-center justify-center">
                                 <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center backdrop-blur hover:scale-110 transition-transform cursor-pointer">
                                     <Play fill="white" className="text-white ml-1" size={32} />
                                 </div>
                             </div>

                             {/* DQS Badge Overlay (Floating for Video) */}
                            <div className="absolute bottom-4 right-4 z-20 max-w-[200px] cursor-pointer" onClick={() => setShowFullAnalysis(!showFullAnalysis)}>
                                {showFullAnalysis ? (
                                    <div className="bg-slate-900/90 backdrop-blur-md p-2 rounded-lg border border-slate-700 shadow-2xl animate-in slide-in-from-bottom-2">
                                        <AnalysisBadge analysis={post.analysis} expanded={true} />
                                    </div>
                                ) : (
                                    <div className="flex items-center gap-2 bg-slate-900/60 backdrop-blur-md p-1.5 rounded-full border border-slate-700/50 hover:bg-slate-900 transition-colors">
                                        <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs ${post.analysis.score >= 80 ? 'bg-emerald-500 text-white' : post.analysis.score >= 50 ? 'bg-amber-500 text-black' : 'bg-red-500 text-white'}`}>
                                            {post.analysis.score}
                                        </div>
                                        <span className="text-[10px] font-bold text-white uppercase pr-2">Discourse Score</span>
                                    </div>
                                )}
                            </div>

                            {/* Actions Overlay Row */}
                            <div className="absolute bottom-4 left-4 z-20 flex flex-col gap-4">
                                <button className="text-white hover:text-primary-400 transition-colors drop-shadow-md">
                                    <Bookmark size={24} />
                                    <span className="text-[10px] block text-center mt-1">{post.bookmarks}</span>
                                </button>
                                <button className="text-white hover:text-primary-400 transition-colors drop-shadow-md">
                                    <Share2 size={24} />
                                    <span className="text-[10px] block text-center mt-1">Share</span>
                                </button>
                            </div>
                        </div>
                    </div>
                ) : (
                    /* TEXT LAYOUT - Uses unified PostCard in Hero Mode */
                    <PostCard post={post} isHero={true} />
                )}
            </div>

            {/* BOTTOM HALF: Underpost Region */}
            <div className="flex-1 bg-slate-900 relative z-10 border-t border-slate-800 shadow-[0_-10px_40px_-15px_rgba(0,0,0,0.5)] min-h-0">
                 <PostInteractionPanel post={post} onCommentClick={onCommentClick} isFeedMode={true} />
            </div>

        </div>
    );
};
