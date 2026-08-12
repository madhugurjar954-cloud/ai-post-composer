import '../styles/globals.css'
import { createClient } from '@supabase/supabase-js'
import { SupabaseProvider } from '../lib/supabaseClient'

function MyApp({ Component, pageProps }) {
  return (
    <SupabaseProvider>
      <Component {...pageProps} />
    </SupabaseProvider>
  )
}

export default MyApp
