-- Supabase schema for Trackly (Subscriptions & Medications)

create table if not exists users (
  id uuid primary key default gen_random_uuid(),
  email text unique,
  created_at timestamptz default now()
);

create table if not exists subscriptions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete cascade,
  name text not null,
  price numeric,
  currency text default 'USD',
  cycle_type text, -- monthly, yearly, weekly, custom
  next_date date,
  auto_renew boolean default true,
  cancel_url text,
  notes text,
  created_at timestamptz default now()
);

create table if not exists medications (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete cascade,
  name text not null,
  dosage text,
  times text[], -- array of times in HH:MM
  days_of_week int[], -- 0-6
  start_date date,
  end_date date,
  refill_threshold int,
  notes text,
  created_at timestamptz default now()
);

create table if not exists reminders (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete cascade,
  parent_type text, -- 'subscription' or 'medication'
  parent_id uuid,
  reminder_time timestamptz,
  channel text, -- email, sms, ics
  sent boolean default false,
  created_at timestamptz default now()
);
