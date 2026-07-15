create table if not exists profile (
    id int primary key default 1,
    name text default '',
    age int default 0,
    height_in_cm int default 0,
    location text default '',
    water_target_litres numeric default 1.0,
    workout_sessions_target int default 1,
    productivity_minutes_target int default 10
);

create table if not exists logs (
    id uuid primary key default gen_random_uuid(),
    category text not null,
    log_date date not null,
    log_time text not null default '00:00:00',
    payload jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create index if not exists log_category_date_idx on logs (category, log_date)

create table if not exists chat_messages (
    id uuid primary key default gen_random_uuid(),
    role text not null,
    content text not null,
    created_at timestamptz not null default now()
);