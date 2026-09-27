
import { createClient, SupabaseClient } from '@supabase/supabase-js';

// Derived from your connection string: 
// postgres://postgres:...@db.zmvcfdaukpbtimlotaep.supabase.co:5432...
const PROJECT_URL = 'https://zmvcfdaukpbtimlotaep.supabase.co';
const STORAGE_KEY = 'tatsat_supabase_key';

// Provided by user
const PROVIDED_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InptdmNmZGF1a3BidGltbG90YWVwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY0ODEwMTYsImV4cCI6MjA4MjA1NzAxNn0.XopdP2-wxodphHWAJqtpriXxF-Q8Yf6yZGSiXH27NAc';

let supabaseInstance: SupabaseClient | null = null;

export const getSupabase = (): SupabaseClient | null => {
  if (supabaseInstance) return supabaseInstance;

  // 1. Try Environment Variable, then the Provided Key
  let key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || PROVIDED_ANON_KEY;
  
  // 2. Try Local Storage (Runtime override if needed)
  if (!key && typeof window !== 'undefined') {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) key = stored;
  }

  if (PROJECT_URL && key) {
    try {
        supabaseInstance = createClient(PROJECT_URL, key);
    } catch (e) {
        console.error("Invalid Supabase Client config", e);
        return null;
    }
  }
  
  return supabaseInstance;
};

export const saveKeyAndInit = (key: string): boolean => {
    if (!key.startsWith('eyJ')) return false; // Basic JWT check
    try {
        localStorage.setItem(STORAGE_KEY, key);
        supabaseInstance = createClient(PROJECT_URL, key);
        return true;
    } catch (e) {
        return false;
    }
}

export const isSupabaseConfigured = () => !!getSupabase();