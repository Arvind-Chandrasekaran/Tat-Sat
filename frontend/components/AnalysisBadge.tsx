
import React, { useState } from 'react';
import { AnalysisResult } from '../types';
import { ShieldCheck, ShieldAlert, Scale, Brain, MessageCircle, Activity, Lightbulb, Link as LinkIcon, ExternalLink, Terminal, GitMerge } from 'lucide-react';

interface AnalysisBadgeProps {
  analysis: AnalysisResult;
  expanded?: boolean;
}

export const AnalysisBadge: React.FC<AnalysisBadgeProps> = ({ analysis, expanded = false }) => {
  const { score, reasoning, suggestion, tags, scores, toulmin, fallacies, verifiedSources, semanticConnections, grice } = analysis;
  const [showDebug, setShowDebug] = useState(false);

  let colorClass = 'text-gray-400 border-gray-700 bg-gray-900/50';
  let scoreColor = 'text-gray-400';
  
  if (score >= 80) {
    colorClass = 'text-emerald-400 border-emerald-900/50 bg-emerald-950/30';
    scoreColor = 'text-emerald-400';
  } else if (score >= 50) {
    colorClass = 'text-amber-400 border-amber-900/50 bg-amber-950/30';
    scoreColor = 'text-amber-400';
  } else {
    colorClass = 'text-rose-400 border-rose-900/50 bg-rose-950/30';
    scoreColor = 'text-rose-400';
  }

  // Helper for Toulmin items
  const ToulminItem = ({ active, label }: { active: boolean, label: string }) => (
      <div className={`px-2 py-1 rounded text-[10px] uppercase font-bold border ${active ? 'bg-indigo-950/50 border-indigo-500/50 text-indigo-300' : 'bg-slate-900 border-slate-800 text-slate-600'}`}>
          {label}
      </div>
  );

  return (
    <div className={`flex flex-col gap-2 rounded-lg border ${colorClass} p-3 transition-all duration-300`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
            <div className={`relative flex items-center justify-center w-10 h-10 rounded-full border-2 ${colorClass.split(' ')[1]} font-bold text-sm`}>
                {score}
            </div>
            <div className="flex flex-col">
                <span className="text-xs font-semibold uppercase tracking-wider opacity-70">Discourse Score (DQS)</span>
                <span className="text-sm font-medium">{score >= 80 ? 'High Quality' : score >= 50 ? 'Moderate' : 'Low Effort'}</span>
            </div>
        </div>
        <div className="flex gap-1">
            {tags.slice(0, 2).map((tag, i) => (
                <span key={i} className="text-[10px] px-2 py-1 rounded-full bg-slate-800/80 border border-slate-700 text-slate-300">
                    {tag}
                </span>
            ))}
        </div>
      </div>
      
      {expanded && scores && (
          <div className="mt-3 space-y-3 border-t border-slate-700/50 pt-3">
            {/* Component Scores Grid */}
            <div className="grid grid-cols-4 gap-2">
                <ScoreItem label="Arg Struct" value={scores.ASQ} icon={Scale} />
                <ScoreItem label="Fallacy Free" value={scores.FS} icon={ShieldCheck} />
                <ScoreItem label="Cooperation" value={scores.CPS} icon={MessageCircle} />
                <ScoreItem label="Tone" value={scores.ETS} icon={Activity} />
            </div>

            {/* Toulmin Visualization */}
            {toulmin && (
                <div className="bg-slate-950/50 rounded p-2 border border-slate-800">
                    <span className="text-[10px] text-slate-500 uppercase font-semibold mb-2 block">Structure (Toulmin)</span>
                    <div className="flex flex-wrap gap-1.5">
                        <ToulminItem active={toulmin.claim} label="Claim" />
                        <ToulminItem active={toulmin.grounds} label="Grounds" />
                        <ToulminItem active={toulmin.warrant} label="Warrant" />
                        <ToulminItem active={toulmin.backing} label="Backing" />
                        <ToulminItem active={toulmin.qualifier} label="Qualifier" />
                        <ToulminItem active={toulmin.rebuttal} label="Rebuttal" />
                    </div>
                </div>
            )}
            
            {/* Verified Sources (Grounding) */}
            {verifiedSources && verifiedSources.length > 0 && (
                <div className="bg-emerald-950/20 border border-emerald-900/30 rounded p-2">
                    <div className="flex items-center gap-2 mb-1">
                        <LinkIcon size={12} className="text-emerald-500" />
                        <span className="text-[10px] font-bold text-emerald-400 uppercase">Verified via Google</span>
                    </div>
                    <div className="flex flex-col gap-1">
                        {verifiedSources.map((source, idx) => (
                            <a key={idx} href={source.uri} target="_blank" rel="noopener noreferrer" className="text-[10px] text-emerald-300 hover:text-emerald-200 hover:underline truncate flex items-center gap-1">
                                {source.title} <ExternalLink size={8} />
                            </a>
                        ))}
                    </div>
                </div>
            )}

            {/* Fallacies Warning */}
            {fallacies && fallacies.length > 0 && (
                <div className="bg-rose-950/20 border border-rose-900/30 rounded p-2 flex items-start gap-2">
                    <ShieldAlert size={14} className="text-rose-500 mt-0.5" />
                    <div className="flex flex-col">
                        <span className="text-[10px] font-bold text-rose-400 uppercase">Fallacies Detected</span>
                        <span className="text-xs text-rose-300">{fallacies.join(", ")}</span>
                    </div>
                </div>
            )}

            {/* Reasoning & Suggestion */}
            <div className="space-y-2">
                <div className="text-sm opacity-90 italic border-l-2 border-slate-700 pl-2">
                   "{reasoning}"
                </div>
                
                {suggestion && (
                    <div className="bg-primary-900/20 border border-primary-900/30 p-2 rounded flex gap-2">
                        <Lightbulb size={16} className="text-primary-400 shrink-0 mt-0.5" />
                        <div className="flex flex-col">
                             <span className="text-[10px] font-bold text-primary-400 uppercase">Coach Tip</span>
                             <span className="text-xs text-primary-200">{suggestion}</span>
                        </div>
                    </div>
                )}
            </div>
            
            {/* Toggle Debug View */}
            <button 
                onClick={(e) => { e.stopPropagation(); setShowDebug(!showDebug); }}
                className="w-full py-1 bg-slate-800 text-slate-500 text-[10px] rounded uppercase font-bold flex items-center justify-center gap-1 hover:bg-slate-700 hover:text-slate-300"
            >
                <Terminal size={10} />
                {showDebug ? 'Hide' : 'Show'} Raw Analysis Data
            </button>

            {showDebug && (
                 <div className="bg-black/50 p-2 rounded border border-slate-800 font-mono text-[9px] text-slate-400 overflow-x-auto">
                     <div className="mb-2">
                         <span className="text-emerald-500 font-bold block mb-1 flex items-center gap-1"><GitMerge size={8}/> Stored Semantic Connections:</span>
                         {semanticConnections && semanticConnections.length > 0 ? (
                             <ul className="list-disc pl-3">
                                 {semanticConnections.map((conn, i) => (
                                     <li key={i}>{conn.postId}: <span className="text-emerald-300">{conn.type}</span></li>
                                 ))}
                             </ul>
                         ) : (
                             <span className="text-slate-600 italic">None calculated or stored.</span>
                         )}
                     </div>
                     <pre>{JSON.stringify({ toulmin, grice, fallacies }, null, 2)}</pre>
                 </div>
            )}
          </div>
      )}
    </div>
  );
};

const ScoreItem = ({ label, value, icon: Icon }: { label: string, value: number, icon: any }) => {
    let color = 'text-slate-400';
    if(value > 80) color = 'text-emerald-400';
    else if(value < 50) color = 'text-rose-400';
    
    return (
        <div className="flex flex-col items-center bg-slate-900/80 rounded p-2 border border-slate-800">
            <Icon size={14} className={`mb-1 ${color}`} />
            <span className={`text-sm font-bold ${color}`}>{value}</span>
            <span className="text-[9px] text-slate-500 uppercase text-center leading-none mt-1">{label}</span>
        </div>
    );
};
