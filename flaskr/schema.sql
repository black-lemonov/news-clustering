DROP TABLE IF EXISTS cluster;
DROP TABLE IF EXISTS article;

CREATE TABLE cluster (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    summary TEXT,
    first_article_date TIMESTAMP,
    last_article_date TIMESTAMP
);

CREATE TABLE article (
    url TEXT PRIMARY KEY,
    title TEXT,
    date TIMESTAMP,
    content TEXT,
    cluster_id INTEGER DEFAULT -1,
    FOREIGN KEY (cluster_id) REFERENCES cluster(id)
);

