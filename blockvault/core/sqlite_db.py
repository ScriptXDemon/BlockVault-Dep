from __future__ import annotations
import sqlite3
import json
import os
from typing import Any, Dict, Optional, Iterator
from contextlib import contextmanager


class SQLiteCollection:
    def __init__(self, db_path: str, collection_name: str):
        self.db_path = db_path
        self.collection_name = collection_name
        self._ensure_table()

    def _ensure_table(self):
        """Create the table if it doesn't exist"""
        with self._get_connection() as conn:
            conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.collection_name} (
                    id TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    @contextmanager
    def _get_connection(self):
        """Get a database connection with proper error handling"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _serialize_doc(self, doc: Dict[str, Any]) -> str:
        """Serialize document to JSON string"""
        return json.dumps(doc, default=str)

    def _deserialize_doc(self, data: str) -> Dict[str, Any]:
        """Deserialize JSON string to document"""
        return json.loads(data)

    def _match(self, doc: Dict[str, Any], flt: Dict[str, Any]) -> bool:
        """Check if document matches filter"""
        return all(doc.get(k) == v for k, v in flt.items())

    def find_one(self, flt: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find one document matching the filter"""
        with self._get_connection() as conn:
            cursor = conn.execute(f"SELECT data FROM {self.collection_name}")
            for row in cursor:
                doc = self._deserialize_doc(row['data'])
                if self._match(doc, flt):
                    return doc.copy()
        return None

    def find(self, flt: Optional[Dict[str, Any]] = None) -> Iterator[Dict[str, Any]]:
        """Find all documents matching the filter"""
        flt = flt or {}
        with self._get_connection() as conn:
            cursor = conn.execute(f"SELECT data FROM {self.collection_name}")
            for row in cursor:
                doc = self._deserialize_doc(row['data'])
                if self._match(doc, flt):
                    yield doc.copy()

    def insert_one(self, doc: Dict[str, Any]) -> '_InsertResult':
        """Insert one document"""
        import time
        import uuid
        
        # Generate a unique ID
        doc_id = str(uuid.uuid4())
        doc_copy = dict(doc)
        doc_copy['_id'] = doc_id
        
        with self._get_connection() as conn:
            conn.execute(
                f"INSERT INTO {self.collection_name} (id, data) VALUES (?, ?)",
                (doc_id, self._serialize_doc(doc_copy))
            )
            conn.commit()
        
        return self._InsertResult(doc_id)

    def update_one(self, flt: Dict[str, Any], update: Dict[str, Any], upsert: bool = False):
        """Update one document matching the filter"""
        with self._get_connection() as conn:
            # Find the document to update
            cursor = conn.execute(f"SELECT id, data FROM {self.collection_name}")
            doc_id = None
            doc = None
            
            for row in cursor:
                current_doc = self._deserialize_doc(row['data'])
                if self._match(current_doc, flt):
                    doc_id = row['id']
                    doc = current_doc
                    break
            
            if doc_id is None:
                if not upsert:
                    return
                # Create new document
                new_doc = dict(flt)
                if "$setOnInsert" in update:
                    new_doc.update(update["$setOnInsert"])
                if "$set" in update:
                    new_doc.update(update["$set"])
                
                import uuid
                doc_id = str(uuid.uuid4())
                new_doc['_id'] = doc_id
                
                conn.execute(
                    f"INSERT INTO {self.collection_name} (id, data) VALUES (?, ?)",
                    (doc_id, self._serialize_doc(new_doc))
                )
            else:
                # Update existing document
                if "$set" in update:
                    doc.update(update["$set"])
                
                conn.execute(
                    f"UPDATE {self.collection_name} SET data = ? WHERE id = ?",
                    (self._serialize_doc(doc), doc_id)
                )
            
            conn.commit()

    def delete_one(self, flt: Dict[str, Any]):
        """Delete one document matching the filter"""
        with self._get_connection() as conn:
            cursor = conn.execute(f"SELECT id, data FROM {self.collection_name}")
            for row in cursor:
                doc = self._deserialize_doc(row['data'])
                if self._match(doc, flt):
                    conn.execute(f"DELETE FROM {self.collection_name} WHERE id = ?", (row['id'],))
                    conn.commit()
                    break

    class _InsertResult:
        def __init__(self, inserted_id: str):
            self.inserted_id = inserted_id


class SQLiteDB:
    def __init__(self, db_path: str = "blockvault.db"):
        self.db_path = db_path
        self._collections: Dict[str, SQLiteCollection] = {}

    def __getitem__(self, collection_name: str) -> SQLiteCollection:
        """Get a collection by name"""
        if collection_name not in self._collections:
            self._collections[collection_name] = SQLiteCollection(self.db_path, collection_name)
        return self._collections[collection_name]


def get_sqlite_db(db_path: str = "blockvault.db") -> SQLiteDB:
    """Get a SQLite database instance"""
    return SQLiteDB(db_path)
