CREATE TABLE IF NOT EXISTS "Articles" (
    "url"	TEXT,
    "title"	TEXT,
    "description"	TEXT,
    "date"	TEXT,
    "cluster_n"	INTEGER DEFAULT -1,
    PRIMARY KEY("url")
)