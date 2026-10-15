
import React, { useState, useEffect, useRef } from 'react';
import { Sidebar } from './components/Sidebar';
import { PostCard } from './components/PostCard';
import { CreatePost } from './components/CreatePost';
import { PostDetail } from './components/PostDetail';
import { FeedSlide } from './components/FeedSlide';
import { NavigationTab, Post, PostType, AnalysisResult } from './types';
import { backend } from './services/backend'; 
import { saveKeyAndInit } from './services/supabaseClient';
import { Filter, Database, Server, AlertTriangle, Key, ChevronRight, RefreshCcw, Terminal, X } from 'lucide-react';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<NavigationTab>(NavigationTab.FEED);
  const [posts, setPosts] = useState<Post[]>([]);
  const [nextFeedCursor, setNextFeedCursor] = useState<string | null>(null);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [isInitializing, setIsInitializing] = useState(true);
  const [semanticStatus, setSemanticStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('loading');
  const [bootLogs, setBootLogs] = useState<string[]>([]);
  const [errorDetails, setErrorDetails] = useState<{type: string, msg: string} | null>(null);
  const [apiKeyInput, setApiKeyInput] = useState('');
  
  // Debug / Logs Overlay
  const [showLogs, setShowLogs] = useState(false);
  const logsEndRef = useRef<HTMLDivElement>(null);

  const initializedRef = useRef(false);
  const [postStack, setPostStack] = useState<Post[]>([]);

  // Function to add logs (used by backend)
  const addLog = (msg: string) => {
      setBootLogs(prev => {
          const newLogs = [...prev, msg];
          return newLogs.slice(-50); // Keep last 50 logs
      });
  };

  const runBootstrap = async () => {
        setSemanticStatus('loading');
        addLog("Initializing TatSat Client...");
        setErrorDetails(null);
        
        try {
            await backend.initialize(addLog);
            const feed = await backend.getFeed();
            setPosts(feed.feed);
            setNextFeedCursor(feed.next_cursor);
            setSemanticStatus('success');
            setIsInitializing(false);
        } catch (e: any) {
            console.error(e);
            setSemanticStatus('error');
            
            if (e.message === "MISSING_CREDENTIALS") {
                setErrorDetails({ type: "MISSING_CREDENTIALS", msg: "API Key Required" });
                addLog("FATAL: Credentials Missing.");
            } 
            else if (e.message === "INVALID_KEY") {
                setErrorDetails({ type: "INVALID_KEY", msg: "The provided API Key is invalid or expired." });
            }
            else if (e.message === "MISSING_TABLES") {
                setErrorDetails({ type: "MISSING_TABLES", msg: "Database tables not found. Did you run schema_unified.sql from the project root?" });
            }
            else {
                setErrorDetails({ type: "CONNECTION_FAILED", msg: e.message || "Connection Failed" });
                addLog("CRITICAL: Connection Failed.");
            }
        }
  };

  useEffect(() => {
    if (initializedRef.current) return;
    initializedRef.current = true;
    runBootstrap();
  }, []); 

  // Auto-scroll logs
  useEffect(() => {
      if(showLogs && logsEndRef.current) {
          logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
      }
  }, [bootLogs, showLogs]);

  useEffect(() => {
     if (isInitializing || semanticStatus !== 'success') return;
     const refresh = async () => {
         const mode = activeTab === NavigationTab.EXPLORE ? 'HIGH_QUALITY' : 'ALL';
         const feed = await backend.getFeed(mode);
         setPosts(feed.feed);
         setNextFeedCursor(feed.next_cursor);
     };
     refresh();
  }, [activeTab, isInitializing, semanticStatus]);

  const loadMorePosts = async () => {
      if (!nextFeedCursor || isLoadingMore) return;
      setIsLoadingMore(true);
      try {
          const filter = activeTab === NavigationTab.EXPLORE ? 'HIGH_QUALITY' : 'ALL';
          const page = await backend.getFeed(filter, nextFeedCursor);
          setPosts(prev => [...prev, ...page.feed]);
          setNextFeedCursor(page.next_cursor);
      } catch (error) {
          addLog(`Feed pagination failed: ${error}`);
      } finally {
          setIsLoadingMore(false);
      }
  };
  
  const handlePostCreate = async (content: string, _type: PostType, _analysis: AnalysisResult, mediaFile?: File) => {
    try {
        const queued = await backend.createPost(content, mediaFile);
        addLog(`Post queued successfully: ${queued.queue_id}`);
        setActiveTab(NavigationTab.FEED);
    } catch(e) {
        addLog(`Post Error: ${e}`);
        throw e;
    }
  };

  const handleSaveKey = () => {
      const success = saveKeyAndInit(apiKeyInput.trim());
      if (success) {
          runBootstrap();
      } else {
          alert("Invalid Key Format. It should look like 'eyJh...'");
      }
  };

  const handleReindex = async () => {
      // Immediate visual feedback
      setShowLogs(true);
      addLog("Manual Graph Re-Index Triggered...");
      
      try {
          const updates = await backend.reanalyzeGraph();
          if (updates > 0) {
              const feed = await backend.getFeed();
              setPosts(feed.feed);
              addLog(`Feed refreshed. Graph updated.`);
          }
      } catch (e) {
          addLog(`Re-Index failed: ${e}`);
      }
  };

  const openPost = (post: Post) => { setPostStack([post]); };

  const pushCommentAsPost = (comment: Post) => {
      setPostStack((prev) => [...prev, comment]);
  };

  const closeTopPost = () => {
      setPostStack((prev) => prev.length <= 1 ? [] : prev.slice(0, -1));
  };

  const currentPost = postStack.length > 0 ? postStack[postStack.length - 1] : null;
  const activePostData = currentPost 
    ? (posts.find(p => p.id === currentPost.id) || currentPost) 
    : null;

  if (semanticStatus === 'error') {
      return (
          <div className="min-h-[100dvh] bg-slate-950 flex items-center justify-center p-4">
              <div className="bg-slate-900 border border-red-900/50 p-6 md:p-8 rounded-2xl max-w-md w-full shadow-2xl relative overflow-hidden">
                  <div className="absolute top-0 left-0 w-full h-1 bg-red-600"></div>
                  
                  <div className="flex items-center gap-3 text-red-500 mb-4">
                      <AlertTriangle size={32} />
                      <h2 className="text-xl font-bold">System Offline</h2>
                  </div>
                  
                  <p className="text-slate-300 mb-6 leading-relaxed text-sm md:text-base">
                      {errorDetails?.msg || "The Knowledge Graph could not be reached."}
                  </p>

                  {(errorDetails?.type === "MISSING_CREDENTIALS" || errorDetails?.type === "INVALID_KEY") && (
                      <div className="mb-6 bg-slate-950 p-4 rounded-lg border border-slate-800">
                          <label className="text-xs text-slate-500 uppercase font-bold mb-2 block">Enter Supabase Anon Key</label>
                          <p className="text-[10px] text-slate-500 mb-3">Found in Dashboard &gt; Project Settings &gt; API</p>
                          <div className="flex gap-2">
                              <input 
                                type="password" 
                                placeholder="eyJh..."
                                className="flex-1 bg-slate-900 border border-slate-700 rounded px-3 py-2 text-sm text-white focus:border-primary-500 outline-none"
                                value={apiKeyInput}
                                onChange={(e) => setApiKeyInput(e.target.value)}
                              />
                              <button 
                                onClick={handleSaveKey}
                                className="bg-primary-600 hover:bg-primary-500 text-white px-3 rounded flex items-center"
                              >
                                  <ChevronRight size={18} />
                              </button>
                          </div>
                      </div>
                  )}
                  
                  {errorDetails?.type === "MISSING_TABLES" && (
                      <div className="mb-6 bg-amber-950/30 p-4 rounded-lg border border-amber-900/50">
                          <h4 className="text-amber-500 font-bold text-sm mb-2">Schema Required</h4>
                          <p className="text-xs text-amber-200 mb-2">The database exists but is empty. Please run <code>schema_unified.sql</code> from the project root in the Supabase SQL Editor.</p>
                      </div>
                  )}

                  <div className="bg-black/50 p-4 rounded-lg font-mono text-xs text-slate-500 mb-6 hidden md:block">
                      {bootLogs.slice(-3).map((l, i) => <div key={i}>{`> ${l}`}</div>)}
                  </div>
                  
                  <button onClick={() => { setIsInitializing(true); runBootstrap(); }} className="w-full py-3 bg-slate-800 hover:bg-slate-700 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-2">
                      <RefreshCcw size={16} /> Retry Connection
                  </button>
              </div>
          </div>
      );
  }

  return (
    <div className="h-[100dvh] bg-slate-950 text-slate-200 font-sans flex flex-col md:flex-row relative overflow-hidden">
      
      {/* Sidebar / Bottom Nav */}
      <Sidebar 
        activeTab={activeTab} 
        onTabChange={setActiveTab} 
        semanticStatus={semanticStatus} 
        onShowLogs={() => setShowLogs(true)}
        onReindex={handleReindex}
      />

      <main className="flex-1 w-full relative flex flex-col h-full overflow-hidden pb-16 md:pb-0">
        
        {/* Mobile Header (Now Visible in all modes, overlay in Feed) */}
        <div className={`md:hidden flex items-center justify-between px-4 py-3 z-30 shrink-0 ${
            activeTab === NavigationTab.FEED 
            ? 'absolute top-0 left-0 right-0 bg-gradient-to-b from-black/80 to-transparent pt-4' 
            : 'bg-slate-950/95 backdrop-blur border-b border-slate-900 relative'
        }`}>
            <div className="flex items-center gap-2">
                <h1 className="text-lg font-bold text-slate-100 drop-shadow-md">TatSat</h1>
                <div className={`w-2 h-2 rounded-full shadow-sm ${
                    semanticStatus === 'success' ? 'bg-emerald-500' : 
                    semanticStatus === 'loading' ? 'bg-amber-500 animate-pulse' : 'bg-rose-500'
                }`} />
            </div>

            <div className="flex items-center gap-3">
                 <button 
                    onClick={handleReindex} 
                    className="p-2 text-slate-300 hover:text-white bg-slate-800/50 backdrop-blur rounded-full border border-white/10"
                    title="Re-Index"
                 >
                    <RefreshCcw size={16} className={semanticStatus === 'loading' ? 'animate-spin' : ''} />
                 </button>
                 
                 <button 
                    onClick={() => setShowLogs(true)} 
                    className="p-2 text-slate-300 hover:text-white bg-slate-800/50 backdrop-blur rounded-full border border-white/10"
                    title="View Logs"
                 >
                    <Terminal size={16} />
                 </button>
            </div>
        </div>

        {activeTab === NavigationTab.CREATE ? (
            <div className="p-0 md:p-8 max-w-2xl mx-auto w-full h-full overflow-y-auto">
                <CreatePost 
                    onPostCreate={handlePostCreate} 
                    onCancel={() => setActiveTab(NavigationTab.FEED)} 
                />
            </div>
        ) : activeTab === NavigationTab.FEED ? (
            // TIKTOK STYLE FEED - Fits exactly in available space
            <div className="w-full h-full overflow-y-scroll snap-y snap-mandatory bg-black scrollbar-hide">
                 {!isInitializing && posts.length === 0 && (
                    <div className="h-full w-full flex items-center justify-center text-slate-500">
                        <p>No discourse found in this sector.</p>
                    </div>
                 )}
                 {posts.map(post => (
                    <FeedSlide key={post.id} post={post} onCommentClick={pushCommentAsPost} />
                 ))}
                 {nextFeedCursor && (
                    <div className="snap-start flex justify-center p-6 bg-black">
                        <button onClick={loadMorePosts} disabled={isLoadingMore} className="px-4 py-2 rounded-lg bg-slate-800 text-slate-200 disabled:opacity-50">
                            {isLoadingMore ? 'Loading...' : 'Load more'}
                        </button>
                    </div>
                 )}
            </div>
        ) : (
          // STANDARD LIST VIEW
          <div className="flex-1 overflow-y-auto scrollbar-thin">
             <div className="p-4 md:p-8 max-w-2xl mx-auto w-full">
                <div className="hidden md:flex justify-between items-center mb-6">
                  <h2 className="text-2xl font-bold text-white">
                    {activeTab === NavigationTab.EXPLORE ? 'High Discourse' : 'Your Stream'}
                  </h2>
                  <div className="flex gap-2">
                     <button className="p-2 text-slate-400 hover:text-white bg-slate-900 rounded-lg border border-slate-800">
                        <Filter size={18} />
                     </button>
                  </div>
                </div>
                
                <div className="space-y-4 md:space-y-6 pb-20">
                    {posts.map(post => (
                        <PostCard 
                            key={post.id} 
                            post={post} 
                            onClick={() => openPost(post)}
                        />
                    ))}
                </div>
                {nextFeedCursor && (
                    <button onClick={loadMorePosts} disabled={isLoadingMore} className="w-full py-3 rounded-lg bg-slate-800 text-slate-200 disabled:opacity-50">
                        {isLoadingMore ? 'Loading...' : 'Load more'}
                    </button>
                )}
             </div>
          </div>
        )}
      </main>

      {/* STACKED MODAL VIEW */}
      {activePostData && (
        <PostDetail 
            key={activePostData.id}
            post={activePostData} 
            onClose={closeTopPost}
            onCommentClick={pushCommentAsPost}
            isNested={postStack.length > 1}
            allPosts={posts}
        />
      )}

      {/* LOGS OVERLAY */}
      {showLogs && (
          <div className="fixed inset-0 z-[60] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4" onClick={() => setShowLogs(false)}>
              <div className="bg-slate-950 border border-slate-800 w-full max-w-2xl h-[500px] rounded-xl flex flex-col shadow-2xl" onClick={e => e.stopPropagation()}>
                  <div className="flex justify-between items-center p-3 border-b border-slate-800">
                      <div className="flex items-center gap-2 text-emerald-500">
                          <Terminal size={16} />
                          <span className="font-mono text-sm font-bold">System Kernel Logs</span>
                      </div>
                      <div className="flex gap-2">
                          <button onClick={handleReindex} className="px-3 py-1 bg-slate-800 hover:bg-primary-600 text-white text-xs rounded border border-slate-700 transition-colors flex items-center gap-2">
                               <RefreshCcw size={12} /> Re-Index Graph
                          </button>
                          <button onClick={() => setShowLogs(false)} className="text-slate-500 hover:text-white">
                              <X size={18} />
                          </button>
                      </div>
                  </div>
                  <div className="flex-1 overflow-y-auto p-4 font-mono text-xs space-y-1">
                      {bootLogs.map((log, i) => (
                          <div key={i} className="text-slate-300 border-b border-slate-900/50 pb-0.5 mb-0.5">
                              <span className="text-slate-600 select-none mr-2">$</span>
                              {log}
                          </div>
                      ))}
                      <div ref={logsEndRef} />
                  </div>
              </div>
          </div>
      )}
    </div>
  );
};

export default App;
