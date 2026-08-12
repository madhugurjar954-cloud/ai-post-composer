import { createContext, useContext } from 'react'
import { createClient } from '@supabase/supabase-js'

const SupabaseContext = createContext(null)

export function SupabaseProvider({ children }) {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || ''
  const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || ''
  const supabase = createClient(supabaseUrl, supabaseAnonKey)
  return (
    <SupabaseContext.Provider value={supabase}>
      {children}
    </SupabaseContext.Provider>
  )
}

export function useSupabase() {
  return useContext(SupabaseContext)
}
