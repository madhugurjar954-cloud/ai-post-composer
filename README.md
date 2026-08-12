# Trackly — Subscriptions & Medication Reminders (Scaffold)

This branch contains the initial scaffold for the Trackly app (Next.js + Supabase).

What's included:
- web/: Next.js frontend scaffold (basic pages, Supabase client, Dashboard component)
- db/schema.sql: SQL schema for Supabase tables (users, subscriptions, medications, reminders)

Next steps I will implement:
1) Add add/edit forms for subscriptions and medications.
2) Implement ICS export and QR generation endpoints.
3) Add AI parsing endpoint (OpenAI) to auto-fill subscription entries.
4) Implement scheduled email worker (SendGrid + GitHub Actions) for automated reminders.

How to run locally:
- cd web
- npm install
- Set environment variables: NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY
- npm run dev

Do you want me to continue and implement the add/edit forms and ICS export next? If yes, reply and I will proceed and narrate each commit.
