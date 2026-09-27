
import React, { useState } from 'react';
import { Post, PostType } from '../types';
import { AnalysisBadge } from './AnalysisBadge';
import { MessageSquare, Bookmark, Share2, MoreHorizontal, Play, Quote, X } from 'lucide-react';

interface PostCardProps {
  post: Post;
  onClick?: () => void;
  isHero?: boolean;
}

export const PostCard: React.FC<PostCardProps> = ({ post, onClick, isHero = false }) => {
  const [showAnalysis, setShowAnalysis] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);

  const toggleAnalysis = (e: React.MouseEvent) => {
    e.stopPropagation();
    setShowAnalysis(!showAnalysis);
  };

  const handleCardClick = (e: React.MouseEvent) => {
      if (onClick) onClick();
  };

  const handlePlayClick = (e: React.MouseEvent) => {
      e.stopPropagation();
      if(onClick && !isHero) {
        onClick(); 
      } else {
        setIsPlaying(!isPlaying);
      }
  };

  // Editorial Gradient Logic
  const getGradient = (score: number) => {
      if (post.type === PostType.VIDEO) return 'bg-slate-900'; // Videos have their own BG
      if (score >= 80) return 'bg-gradient-to-br from-slate-900 via-slate-900 to-emerald-950/40';
      if (score >= 50) return 'bg-gradient-to-br from-slate-900 via-slate-900 to-amber-950/30';
      return 'bg-gradient-to-br from-slate-900 via-slate-900 to-rose-950/30';
  };

  const containerClasses = isHero 
    ? `h-full w-full flex flex-col relative overflow-hidden ${getGradient(post.analysis.score)}`
    : `rounded-xl border border-slate-800 mb-4 shadow-lg relative overflow-hidden cursor-pointer group hover:border-slate-700 transition-all ${getGradient(post.analysis.score)}`;

  // Mobile Optimized Typography
  const contentClasses = isHero
    ? "text-lg md:text-2xl lg:text-3xl leading-relaxed tracking-wide font-serif text-slate-100"
    : "text-sm md:text-[15px] leading-relaxed font-serif text-slate-200";

  const iconSize = isHero ? 80 : 60; // Smaller quote icon for mobile hero
  const paddingClass = isHero ? "p-4 md:p-8" : "p-4"; // Reduced padding for mobile

  return (
    <div onClick={handleCardClick} className={containerClasses}>
      
      {/* Background Decoration for Text Posts */}
      {post.type === PostType.TEXT && (
          <Quote 
            className={`absolute top-4 left-4 text-slate-800/50 rotate-180 transition-all pointer-events-none z-0`} 
            size={iconSize} 
          />
      )}

      {/* Header */}
      <div className={`flex justify-between items-start z-10 shrink-0 ${paddingClass} pb-0`}>
        <div className="flex gap-3 items-center">
          <img 
            src={post.author.avatar} 
            alt={post.author.name} 
            className={`${isHero ? 'w-10 h-10 md:w-12 md:h-12' : 'w-10 h-10'} rounded-full object-cover border border-slate-700 shadow-sm`}
          />
          <div className="flex flex-col">
            <div className="flex items-center gap-2">
              <span className={`font-bold text-slate-100 ${isHero ? 'text-sm md:text-base' : 'text-sm'} group-hover:text-primary-400 transition-colors`}>{post.author.name}</span>
            </div>
            <span className="text-xs text-slate-400">@{post.author.handle} • {new Date(post.timestamp).toLocaleDateString()}</span>
          </div>
        </div>
        <button className="text-slate-500 hover:text-slate-300 p-1 rounded-full hover:bg-slate-800 transition-colors" onClick={(e) => e.stopPropagation()}>
          <MoreHorizontal size={isHero ? 24 : 20} />
        </button>
      </div>

      {/* Main Content Area */}
      <div className={`flex-1 flex flex-col z-10 min-h-0 ${paddingClass} ${isHero ? 'justify-center' : ''}`}>
        
        {/* Scrollable text container if Hero, otherwise auto */}
        <div className={`flex-1 ${isHero ? 'overflow-y-auto scrollbar-hide flex flex-col justify-center' : ''}`}>
             
             {post.type === PostType.VIDEO && post.thumbnailUrl ? (
                <div className="relative w-full aspect-[16/9] bg-black rounded-lg overflow-hidden mt-2 group/video" onClick={handlePlayClick}>
                    <img 
                    src={post.thumbnailUrl} 
                    alt="Video thumbnail" 
                    className={`w-full h-full object-cover transition-opacity duration-300 ${isPlaying ? 'opacity-30' : 'opacity-80 group-hover/video:opacity-60'}`}
                    />
                    <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                        <div className="bg-white/20 backdrop-blur-sm p-4 rounded-full group-hover/video:bg-white/30 transition-all">
                            <Play fill="white" className="text-white w-8 h-8 ml-1" />
                        </div>
                    </div>
                    {/* Only show caption if NOT in hero mode, as Hero video is handled by FeedSlide separately usually */}
                    {!isHero && (
                        <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/80 to-transparent">
                            <p className="text-white text-sm line-clamp-2">{post.content}</p>
                        </div>
                    )}
                </div>
            ) : (
                <div className={contentClasses}>
                    {post.content}
                </div>
            )}

            {post.topic && post.type === PostType.TEXT && (
                <div className="mt-4 flex gap-2">
                    <span className="text-[10px] font-bold uppercase tracking-widest px-2 py-1 rounded border border-slate-700/50 text-slate-400">
                        {post.topic}
                    </span>
                </div>
            )}
        </div>
      </div>

      {/* Footer / Actions */}
      <div className={`border-t border-slate-800/50 flex justify-between items-center z-10 bg-slate-900/20 backdrop-blur-sm shrink-0 ${paddingClass} py-3`}>
         
         {/* DQS Badge Trigger */}
         <div 
            className="flex items-center gap-3 cursor-pointer group/dqs"
            onClick={toggleAnalysis}
        >
            <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs shadow-lg transition-transform group-hover/dqs:scale-110 ${post.analysis.score >= 80 ? 'bg-emerald-500 text-white' : post.analysis.score >= 50 ? 'bg-amber-500 text-black' : 'bg-red-500 text-white'}`}>
                {post.analysis.score}
            </div>
            <div className="flex flex-col">
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider group-hover/dqs:text-slate-300 transition-colors">Quality</span>
            </div>
        </div>

        <div className="flex gap-4 text-slate-400">
             {!isHero && (
                 <button className="flex items-center gap-1 hover:text-primary-500 transition-colors" onClick={(e) => { e.stopPropagation(); if(onClick) onClick(); }}>
                    <MessageSquare size={18} />
                    <span className="text-xs">{post.comments?.length || 0}</span>
                 </button>
             )}
             <button className="hover:text-primary-500 transition-colors" onClick={(e) => e.stopPropagation()}>
                <Bookmark size={isHero ? 22 : 18} />
             </button>
             <button className="hover:text-primary-500 transition-colors" onClick={(e) => e.stopPropagation()}>
                <Share2 size={isHero ? 22 : 18} />
             </button>
        </div>
      </div>

      {/* Expanded Analysis Popover */}
      {showAnalysis && (
        <div 
            className={`absolute z-30 animate-in fade-in zoom-in-95 duration-200 ${isHero ? 'inset-x-4 bottom-24' : 'inset-0 bg-slate-900/95 backdrop-blur-sm flex items-center justify-center p-4'}`}
            onClick={(e) => isHero ? e.stopPropagation() : toggleAnalysis(e)}
        >
             <div 
                className={`bg-slate-900 border border-slate-700 p-4 rounded-xl shadow-2xl relative overflow-y-auto ${isHero ? 'max-h-[60vh]' : 'w-full max-h-full'}`}
                onClick={(e) => e.stopPropagation()}
             >
                <div className="flex justify-between items-center mb-4">
                    <h4 className="text-sm font-bold text-slate-300 uppercase tracking-wider">Discourse Analysis</h4>
                    <button 
                        onClick={(e) => { e.stopPropagation(); setShowAnalysis(false); }}
                        className="p-1 text-slate-500 hover:text-white bg-slate-800 rounded-full"
                    >
                        <X size={16} />
                    </button>
                </div>
                <AnalysisBadge analysis={post.analysis} expanded={true} />
             </div>
        </div>
      )}
    </div>
  );
};
