from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, cast
import chromadb
from chromadb.utils import embedding_functions
from chromadb.api.types import Embeddable, EmbeddingFunction, Where

from core.config import settings
from tools.database.models import MemoryEntry

class ChromaMemoryRepo:
    def __init__(
        self,
        path: Path = settings.root_path / "memory",
        collection: str = "scalesbot_ltm",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        self.client = chromadb.PersistentClient(path=path)
        self.embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=embedding_model
        )
        self.collection = self.client.get_or_create_collection(
            name=collection,
            embedding_function=cast(EmbeddingFunction[Embeddable], self.embed_fn),
            metadata={"hnsw:space": "cosine"}
        )

    def search(
        self,
        query: str,
        category: Optional[str] = None,
        top_k: int = 3,
        min_score: float = 0.3
    ) -> List[Dict[str, Any]]:
        where = cast(Where, {"category": category}) if category else None
        
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where,
            include=["documents", "metadatas", "distances"]
        )
        
        if not results:
            return []
            
        docs = results.get("documents") or []
        metas = results.get("metadatas") or []
        dists = results.get("distances") or []
        
        if not docs or len(docs[0]) == 0:
            return []
            
        retrieved_docs = docs[0]
        retrieved_metas = metas[0] if len(metas) > 0 else [{}] * len(retrieved_docs)
        retrieved_dists = dists[0] if len(dists) > 0 else [1.0] * len(retrieved_docs)
        
        return [
            {
                "content": doc,
                "meta": meta or {},
                "score": 1 / (1 + dist),
            }
            for doc, meta, dist in zip(retrieved_docs, retrieved_metas, retrieved_dists)
            if (1 / (1 + dist)) >= min_score
        ]

    def store(self, entry: MemoryEntry, entry_id: Optional[str] = None) -> Any:
        similar = self.search(entry.content, top_k=1, min_score=0.95)
        if similar:
            return similar[0]["meta"].get("id", "duplicate")
        
        try:
            count = self.collection.count()
        except Exception:
            count = 0
            
        entry_id = entry_id or f"mem_{count}"
        
        self.collection.add(
            documents=[entry.content],
            ids=[entry_id],
            metadatas=[{
                "category": entry.category,
                "source": entry.source,
                "importance": entry.importance,
                "id": entry_id
            }]
        )
        return entry_id