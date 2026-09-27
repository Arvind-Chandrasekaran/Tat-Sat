
import React, { useState, useEffect } from 'react';
import { PostType, AnalysisResult } from '../types';
import { analyzePostContent } from '../services/geminiService';
import { AnalysisBadge } from './AnalysisBadge';
import { Video, Image, X, Sparkles, Send, Loader2 } from 'lucide-react';

interface CreatePostProps {
  onPostCreate: (content: string, type: PostType, analysis: AnalysisResult, mediaUrl?: string) => Promise<void>;
  onCancel: () => void;
}

export const CreatePost: React.FC<CreatePostProps> = ({ onPostCreate, onCancel }) => {
  const [content, setContent] = useState('');
  const [postType, setPostType] = useState<PostType>(PostType.TEXT);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isPublishing, setIsPublishing] = useState(false);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [mediaPreview, setMediaPreview] = useState<string | null>(null);
  
  // Debounce analysis (Preview only - actual score is finalized on server)
  useEffect(() => {
    const timer = setTimeout(() => {
      if (content.length >= 10) {
        handleAnalyze();
      }
    }, 1500);
    return () => clearTimeout(timer);
  }, [content]);

  const handleAnalyze = async () => {
    if (content.length < 10) return;
    setIsAnalyzing(true);
    // This is a "Preview" call. The real DQS is calculated securely on the server upon submission.
    const result = await analyzePostContent(content, postType === PostType.VIDEO);
    setAnalysis(result);
    setIsAnalyzing(false);
  };

  const handleSubmit = async () => {
    if (!content) return;
    
    let finalAnalysis = analysis;
    if (!finalAnalysis) {
        setIsAnalyzing(true);
        finalAnalysis = await analyzePostContent(content, postType === PostType.VIDEO);
        setAnalysis(finalAnalysis);
        setIsAnalyzing(false);
    }

    if (finalAnalysis && finalAnalysis.score >= 30) {
        setIsPublishing(true);
        try {
            await onPostCreate(content, postType, finalAnalysis, mediaPreview || undefined);
            setContent('');
            setAnalysis(null);
            setMediaPreview(null);
        } catch(e) {
            console.error("Failed to publish", e);
        } finally {
            setIsPublishing(false);
        }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setPostType(PostType.VIDEO);
      const objectUrl = URL.createObjectURL(file);
      setMediaPreview(objectUrl);
    }
  };

  return (
    <div className="bg-slate-900 md:border md:border-slate-700 rounded-xl p-4 md:p-6 mb-8 shadow-2xl relative overflow-hidden h-full md:h-auto flex flex-col">
      <div className="flex justify-between items-center mb-4 shrink-0">
        <h2 className="text-lg font-semibold text-slate-100">Contribute</h2>
        <button onClick={onCancel} className="text-slate-400 hover:text-white p-2 bg-slate-800 rounded-full">
          <X size={20} />
        </button>
      </div>

      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="Share your perspective... Quality is prioritized over virality."
        className="w-full flex-1 bg-slate-950 border border-slate-800 rounded-lg p-3 text-slate-200 placeholder-slate-600 focus:outline-none focus:ring-1 focus:ring-primary-500 resize-none min-h-[150px] md:min-h-[120px]"
        disabled={isPublishing}
      />

      {mediaPreview && (
        <div className="mt-3 relative inline-block shrink-0">
            <div className="w-32 h-48 bg-black rounded-lg overflow-hidden border border-slate-700">
               <div className="w-full h-full flex items-center justify-center text-xs text-slate-500">Video Preview</div>
            </div>
             <button 
                onClick={() => { setMediaPreview(null); setPostType(PostType.TEXT); }}
                className="absolute -top-2 -right-2 bg-slate-800 rounded-full p-1 text-slate-400 hover:text-white border border-slate-600"
             >
                <X size={14} />
             </button>
        </div>
      )}

      {/* AI Feedback Section */}
      <div className="mt-4 min-h-[80px] shrink-0">
        {isAnalyzing ? (
          <div className="flex items-center gap-2 text-primary-500 text-sm animate-pulse">
            <Loader2 size={16} className="animate-spin" />
            <span>Draft analysis in progress...</span>
          </div>
        ) : analysis ? (
          <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
             <div className="flex justify-between items-end mb-2">
                 <span className="text-xs text-slate-500 uppercase tracking-widest">Pre-post Estimate</span>
             </div>
             <AnalysisBadge analysis={analysis} expanded={true} />
             {analysis.score < 50 && (
                <p className="text-xs text-amber-500 mt-2">
                    Tip: Try adding more nuance or supporting evidence to improve visibility.
                </p>
             )}
          </div>
        ) : (
          <div className="text-slate-600 text-sm flex items-center gap-2">
            <Sparkles size={16} />
            <span>AI will analyze your post for quality before publishing.</span>
          </div>
        )}
      </div>

      <div className="flex justify-between items-center mt-4 border-t border-slate-800 pt-3 shrink-0">
        <div className="flex gap-2">
          <label className="p-3 text-slate-400 hover:text-primary-500 bg-slate-800 rounded-full cursor-pointer transition-colors">
            <input type="file" accept="video/*" className="hidden" onChange={handleFileChange} />
            <Video size={20} />
          </label>
        </div>

        <button 
            onClick={handleSubmit}
            disabled={!content || isAnalyzing || (analysis && analysis.score < 30) || isPublishing}
            className={`flex items-center gap-2 px-6 py-3 rounded-full font-medium transition-all ${
                (!content || isAnalyzing || isPublishing) 
                ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                : (analysis && analysis.score < 30)
                    ? 'bg-rose-900/50 text-rose-400 border border-rose-800 cursor-not-allowed' 
                    : 'bg-primary-600 hover:bg-primary-500 text-white shadow-lg shadow-primary-900/20'
            }`}
        >
            {isPublishing ? 'Publishing...' : isAnalyzing ? 'Analyzing...' : (analysis && analysis.score < 30 ? 'Low Quality' : 'Publish')}
            {isPublishing ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
        </button>
      </div>
    </div>
  );
};
