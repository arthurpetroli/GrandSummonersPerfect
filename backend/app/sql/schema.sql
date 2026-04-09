-- Grand Summoners Companion - relational schema (PostgreSQL)
-- Designed for production migration tooling (Alembic/dbmate/etc).

create table if not exists server_regions (
  id smallserial primary key,
  code varchar(16) not null unique,
  name varchar(64) not null
);

create table if not exists users (
  id uuid primary key,
  username varchar(64) not null unique,
  email varchar(255) not null unique,
  password_hash text not null,
  role varchar(32) not null default 'user',
  preferred_region varchar(16) references server_regions(code),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists tags (
  id uuid primary key,
  slug varchar(64) not null unique,
  label varchar(128) not null,
  category varchar(64) not null,
  description text
);

create table if not exists modes (
  id uuid primary key,
  slug varchar(64) not null unique,
  name varchar(128) not null,
  overview text,
  order_index int not null default 0,
  created_at timestamptz not null default now()
);

create table if not exists units (
  id uuid primary key,
  slug varchar(128) not null unique,
  name varchar(128) not null,
  rarity smallint not null,
  element varchar(32) not null,
  race varchar(64) not null,
  role varchar(32) not null,
  damage_type varchar(32) not null,
  server_region varchar(16) not null references server_regions(code),
  strengths text[] not null default '{}',
  limitations text[] not null default '{}',
  best_use text[] not null default '{}',
  weak_in text[] not null default '{}',
  team_dependencies text[] not null default '{}',
  equip_dependencies text[] not null default '{}',
  beginner_value smallint,
  endgame_value smallint,
  sustain_value smallint,
  nuke_value smallint,
  auto_value smallint,
  arena_value smallint,
  released_at date,
  updated_at timestamptz not null default now(),
  search_document tsvector
);

create table if not exists unit_skills (
  id uuid primary key,
  unit_id uuid not null references units(id) on delete cascade,
  skill_type varchar(32) not null,
  name varchar(128) not null,
  description text not null,
  cooldown_seconds int,
  multiplier numeric(8,2),
  notes text,
  unique(unit_id, skill_type)
);

create table if not exists unit_passives (
  id uuid primary key,
  unit_id uuid not null references units(id) on delete cascade,
  name varchar(128) not null,
  description text not null,
  order_index int not null default 0
);

create table if not exists unit_tags (
  id uuid primary key,
  unit_id uuid not null references units(id) on delete cascade,
  tag_id uuid not null references tags(id) on delete cascade,
  confidence smallint not null default 100,
  source_id uuid,
  unique(unit_id, tag_id)
);

create table if not exists unit_equip_slots (
  id uuid primary key,
  unit_id uuid not null references units(id) on delete cascade,
  slot_index smallint not null,
  slot_type varchar(32) not null,
  unique(unit_id, slot_index)
);

create table if not exists equips (
  id uuid primary key,
  slug varchar(128) not null unique,
  name varchar(128) not null,
  slot_type varchar(32) not null,
  category varchar(64) not null,
  cooldown_seconds int not null,
  active_skill text not null,
  passive text,
  stat_hp int,
  stat_atk int,
  stat_def int,
  best_use text[] not null default '{}',
  ranking_overall varchar(8),
  server_region varchar(16) not null references server_regions(code),
  updated_at timestamptz not null default now(),
  search_document tsvector
);

create table if not exists equip_tags (
  id uuid primary key,
  equip_id uuid not null references equips(id) on delete cascade,
  tag_id uuid not null references tags(id) on delete cascade,
  unique(equip_id, tag_id)
);

create table if not exists bosses (
  id uuid primary key,
  slug varchar(128) not null unique,
  name varchar(128) not null,
  mode_id uuid not null references modes(id),
  stage_name varchar(256) not null,
  difficulty varchar(64),
  overview text,
  threats text[] not null default '{}',
  resistances text[] not null default '{}',
  gimmicks text[] not null default '{}',
  special_conditions text[] not null default '{}',
  break_recommendation text,
  updated_at timestamptz not null default now(),
  search_document tsvector
);

create table if not exists boss_mechanics (
  id uuid primary key,
  boss_id uuid not null references bosses(id) on delete cascade,
  key varchar(64) not null,
  description text not null,
  required_utilities text[] not null default '{}',
  order_index int not null default 0
);

create table if not exists stages (
  id uuid primary key,
  boss_id uuid references bosses(id) on delete set null,
  mode_id uuid not null references modes(id),
  code varchar(64),
  name varchar(256) not null,
  difficulty varchar(64),
  notes text
);

create table if not exists comps (
  id uuid primary key,
  slug varchar(128) not null unique,
  name varchar(128) not null,
  mode_id uuid not null references modes(id),
  target_boss_id uuid references bosses(id),
  style varchar(32) not null,
  summary text,
  why_it_works text[] not null default '{}',
  weaknesses text[] not null default '{}',
  required_tags text[] not null default '{}',
  beginner_friendly boolean not null default false,
  created_by uuid references users(id),
  status varchar(32) not null default 'published',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists comp_units (
  id uuid primary key,
  comp_id uuid not null references comps(id) on delete cascade,
  position smallint not null,
  unit_id uuid not null references units(id),
  role_in_comp varchar(128),
  unique(comp_id, position)
);

create table if not exists comp_equips (
  id uuid primary key,
  comp_id uuid not null references comps(id) on delete cascade,
  unit_id uuid references units(id),
  equip_id uuid not null references equips(id),
  priority smallint not null default 1
);

create table if not exists substitutions (
  id uuid primary key,
  entity_type varchar(32) not null,
  from_entity_id uuid not null,
  to_entity_id uuid not null,
  context varchar(128),
  quality_score smallint,
  notes text,
  unique(entity_type, from_entity_id, to_entity_id, context)
);

create table if not exists guides (
  id uuid primary key,
  slug varchar(128) not null unique,
  title varchar(256) not null,
  excerpt text,
  body_markdown text not null,
  mode_id uuid references modes(id),
  status varchar(32) not null default 'published',
  author_id uuid references users(id),
  updated_at timestamptz not null default now(),
  search_document tsvector
);

create table if not exists guide_tags (
  id uuid primary key,
  guide_id uuid not null references guides(id) on delete cascade,
  tag_id uuid not null references tags(id) on delete cascade,
  unique(guide_id, tag_id)
);

create table if not exists tierlists (
  id uuid primary key,
  slug varchar(128) not null unique,
  title varchar(256) not null,
  category varchar(64) not null,
  mode_id uuid references modes(id),
  server_region varchar(16) references server_regions(code),
  version varchar(32) not null,
  methodology_markdown text,
  updated_at timestamptz not null default now()
);

create table if not exists tierlist_entries (
  id uuid primary key,
  tierlist_id uuid not null references tierlists(id) on delete cascade,
  entity_type varchar(32) not null,
  entity_id uuid not null,
  tier varchar(8) not null,
  context_score numeric(6,2),
  reason text not null,
  strong_in text[] not null default '{}',
  weak_in text[] not null default '{}',
  dependencies text[] not null default '{}',
  substitutes text[] not null default '{}',
  beginner_value smallint,
  veteran_value smallint,
  ease_of_use smallint,
  consistency smallint,
  niche_or_generalist varchar(32),
  order_index int not null default 0
);

create table if not exists tierlist_history (
  id uuid primary key,
  tierlist_id uuid not null references tierlists(id) on delete cascade,
  entity_type varchar(32) not null,
  entity_id uuid not null,
  old_tier varchar(8),
  new_tier varchar(8) not null,
  reason text,
  patch_note_id uuid,
  changed_at timestamptz not null default now(),
  changed_by uuid references users(id)
);

create table if not exists ai_presets (
  id uuid primary key,
  slug varchar(128) not null unique,
  name varchar(128) not null,
  purpose varchar(64) not null,
  unit_id uuid references units(id),
  steps text[] not null default '{}',
  notes text[] not null default '{}',
  updated_at timestamptz not null default now()
);

create table if not exists progression_paths (
  id uuid primary key,
  title varchar(128) not null,
  audience varchar(128) not null,
  steps_json jsonb not null,
  updated_at timestamptz not null default now()
);

create table if not exists patch_notes (
  id uuid primary key,
  title varchar(256) not null,
  summary text,
  patch_version varchar(64),
  region varchar(16) references server_regions(code),
  published_at timestamptz not null,
  url text
);

create table if not exists sources (
  id uuid primary key,
  kind varchar(32) not null,
  name varchar(128) not null,
  url text,
  license text,
  trust_level smallint not null default 50,
  active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists source_mappings (
  id uuid primary key,
  source_id uuid not null references sources(id) on delete cascade,
  entity_type varchar(32) not null,
  entity_id uuid,
  source_entity_key varchar(256),
  raw_payload jsonb,
  normalized_payload jsonb,
  validation_status varchar(32) not null default 'pending',
  published boolean not null default false,
  last_seen_at timestamptz,
  updated_at timestamptz not null default now()
);

create table if not exists user_rosters (
  id uuid primary key,
  user_id uuid not null references users(id) on delete cascade,
  name varchar(128) not null default 'default',
  region varchar(16) references server_regions(code),
  unit_ids uuid[] not null default '{}',
  equip_ids uuid[] not null default '{}',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(user_id, name)
);

create table if not exists editorial_changes (
  id uuid primary key,
  entity_type varchar(32) not null,
  entity_id uuid,
  change_type varchar(32) not null,
  diff jsonb not null,
  status varchar(32) not null default 'staged',
  source_ids uuid[] not null default '{}',
  created_by uuid references users(id),
  reviewed_by uuid references users(id),
  created_at timestamptz not null default now(),
  published_at timestamptz
);

create index if not exists idx_units_search_document on units using gin(search_document);
create index if not exists idx_equips_search_document on equips using gin(search_document);
create index if not exists idx_guides_search_document on guides using gin(search_document);
create index if not exists idx_bosses_search_document on bosses using gin(search_document);
create index if not exists idx_tierlist_entries_tierlist on tierlist_entries(tierlist_id, tier, order_index);
create index if not exists idx_comps_mode_boss on comps(mode_id, target_boss_id);
create index if not exists idx_source_mappings_entity on source_mappings(entity_type, entity_id);
