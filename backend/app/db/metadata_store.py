import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS repositories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    root_path TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_id INTEGER NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    relative_path TEXT NOT NULL,
    category TEXT NOT NULL,
    language TEXT,
    size_bytes INTEGER NOT NULL,
    content_hash TEXT NOT NULL,
    UNIQUE(repo_id, relative_path)
);
"""

class MetadataStore:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def upsert_repository(self, name: str, root_path: str) -> int:
        self.conn.execute(
            "INSERT INTO repositories (name, root_path) VALUES (?, ?) "
            "ON CONFLICT(root_path) DO NOTHING",
            (name, root_path),
        )
        self.conn.commit()
        row = self.conn.execute(
            "SELECT id FROM repositories WHERE root_path = ?", (root_path,)
        ).fetchone()
        return row[0]

    def upsert_file(self, repo_id: int, classified_file, content_hash: str) -> bool:
        existing = self.conn.execute(
            "SELECT content_hash FROM files WHERE repo_id = ? AND relative_path = ?",
            (repo_id, classified_file.relative_path),
        ).fetchone()

        changed = existing is None or existing[0] != content_hash

        self.conn.execute(
            """
            INSERT INTO files (repo_id, relative_path, category, language, size_bytes, content_hash)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(repo_id, relative_path) DO UPDATE SET
                category=excluded.category,
                language=excluded.language,
                size_bytes=excluded.size_bytes,
                content_hash=excluded.content_hash
            """,
            (repo_id, classified_file.relative_path, classified_file.category,
             classified_file.language, classified_file.size_bytes, content_hash),
        )
        self.conn.commit()
        return changed

    def list_files(self, repo_id: int):
        return self.conn.execute(
            "SELECT relative_path, category, language, size_bytes, content_hash FROM files WHERE repo_id = ?",
            (repo_id,),
        ).fetchall()

    def close(self):
        self.conn.close()
