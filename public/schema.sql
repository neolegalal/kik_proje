-- NeoLegal Legal Relationship Engine v1.0.0

CREATE TABLE kik_decisions (
    kik_id TEXT PRIMARY KEY,
    slug TEXT UNIQUE NOT NULL,
    search_key TEXT NOT NULL,
    decision_label TEXT NOT NULL,
    filename TEXT NOT NULL,
    court_decision_count INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE court_decisions (
    court_id TEXT PRIMARY KEY,
    slug TEXT UNIQUE NOT NULL,
    filename TEXT NOT NULL
);

CREATE TABLE kik_court_links (
    relationship_id TEXT PRIMARY KEY,
    kik_id TEXT NOT NULL,
    court_id TEXT NOT NULL,
    match_type TEXT NOT NULL,
    match_status TEXT NOT NULL,
    confidence INTEGER NOT NULL,
    source_module TEXT NOT NULL,
    UNIQUE(kik_id, court_id)
);
