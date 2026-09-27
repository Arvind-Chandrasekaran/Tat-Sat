
import React, { useState } from 'react';
import { Post, PostType } from '../types';
import { AnalysisBadge } from './AnalysisBadge';
import { PostInteractionPanel } from './PostInteractionPanel';
import { PostCard } from './PostCard';
import { X, Play, ArrowLeft, MoreHorizontal, Bookmark, Share2 } from 'lucide-react';

interface PostDetailProps {
  post: Post;
  onClose: () => void;
  onCommentClick: (comment: Post) => void;
  isNested?: boolean;
  allPosts?: Post[]; 
}

export const PostDetail: React.FC<PostDetailProps> = ({ post, onClose, onCommentClick, isNested = false }) => {
  const [showFullAnalysis, setShowFullAnalysis] = useState(false);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-sm p-0 md:p-6 animate-in fade-in duration-200">
      <div className="bg-slate-900 w-full md:max-w-4xl h-full md:h-[90vh] md:rounded-2xl border border-slate-800 flex flex-col overflow-hidden shadow-2xl relative">
        
        {/* Navigation Buttons (Overlay) */}
        <div className="absolute top-4 left-4 z-40 flex gap-2">
            {isNested && (
                <button onClick={onClose} className="p-2 bg-black/50 text-white rounded-full hover:bg-slate-800 transition-colors flex items-center gap-1 pr-4 backdrop-blur-md border border-white/10 group">
                    <ArrowLeft size={18} className="group-hover:-translate-x-1 transition-transform" />
                    <span className="text-sm font-medium">Back</span>
                </button>
            )}
        </div>
        
        <button onClick={onClose} className="absolute top-4 right-4 z-40 p-2 bg-black/50 text-white rounded-full hover:bg-slate-800 transition-colors backdrop-blur-md border border-white/10">
            <X size={20} />
        </button>

        {/* Top Section: Post Content (50% height for mobile match) */}
        <div className="h-[50%] md:h-[55%] relative flex flex-col bg-slate-950">
            {post.type === PostType.VIDEO ? (
                // IMMERSIVE VIDEO LAYOUT (Matching FeedSlide)
                <div className="h-full w-full bg-black relative flex flex-col">
                     {/* Header Overlay */}
                    <div className="absolute top-0 left-0 right-0 p-4 pt-16 md:pt-4 z-20 flex justify-between items-start bg-gradient-to-b from-black/80 to-transparent pointer-events-none">
                        <div className="flex gap-3 pointer-events-auto mt-2 md:mt-0">
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
                    </div>

                    {/* Video Content */}
                    <div className="flex-1 relative flex items-center justify-center overflow-hidden">
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

                         {/* DQS Badge Overlay */}
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

                        {/* Actions Overlay */}
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
                // TEXT LAYOUT (Using PostCard in Hero Mode)
                <div className="h-full w-full">
                    <PostCard post={post} isHero={true} />
                </div>
            )}
        </div>

        {/* Bottom Section: Interaction Panel */}
        <div className="flex-1 flex flex-col bg-slate-900 border-t border-slate-800 shadow-[0_-10px_40px_-15px_rgba(0,0,0,0.5)] z-20 relative">
             <PostInteractionPanel post={post} onCommentClick={onCommentClick} isFeedMode={true} />
        </div>
      </div>
    </div>
  );
};
