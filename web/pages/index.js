import Head from 'next/head'
import Dashboard from '../components/Dashboard'

export default function Home() {
  return (
    <div>
      <Head>
        <title>Trackly — Subscriptions & Meds</title>
      </Head>
      <main className="min-h-screen bg-slate-50 p-6">
        <div className="max-w-5xl mx-auto">
          <h1 className="text-3xl font-bold mb-4">Trackly — Subscriptions & Medication Reminders (MVP)</h1>
          <p className="text-slate-600 mb-6">Dashboard scaffold: add subscriptions, medications, export ICS/QR, and enable AI parsing later.</p>
          <Dashboard />
        </div>
      </main>
    </div>
  )
}
