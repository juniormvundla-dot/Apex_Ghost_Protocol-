import math
import re
from datetime import datetime
from pathlib import Path

from storage.db import database_manager

class RAGEngine:
    """
    Offline zero-dependency retrieval engine using TF-IDF cosine-similarity
    to index Shadow Journal captures and active quest lists for local prompt injection.
    """
    def __init__(self):
        self.stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with", "is", "was", "be", "of"}

    def _tokenize(self, text):
        # Convert to lowercase and match word tokens
        words = re.findall(r"\b[a-z0-9]+\b", text.lower())
        return [w for w in words if w not in self.stop_words]

    def _calculate_cosine_similarity(self, vec1, vec2):
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum(vec1[x] * vec2[x] for x in intersection)

        sum1 = sum(val ** 2 for val in vec1.values())
        sum2 = sum(val ** 2 for val in vec2.values())
        denominator = math.sqrt(sum1) * math.sqrt(sum2)

        if not denominator:
            return 0.0
        return float(numerator) / denominator

    def retrieve_context(self, query, limit=5):
        """
        Scan shadow journal logs and database quests, vector ranking the top N matching records.
        """
        database_manager.ensure_ready()
        
        # 1. Gather documents
        documents = []
        
        # Pull shadow journal entries
        journal_rows = database_manager.fetch_all("SELECT content, category, created_at FROM shadow_journal")
        for row in journal_rows:
            documents.append({
                "text": f"[{row['category'].upper()}] {row['content']}",
                "timestamp": row["created_at"],
                "source": "Shadow Journal"
            })
            
        # Pull quests
        quest_rows = database_manager.fetch_all("SELECT title, description, category, status FROM quests")
        for row in quest_rows:
            documents.append({
                "text": f"[QUEST // {row['category'].upper()}] {row['title']} - {row['description']} ({row['status']})",
                "timestamp": "",
                "source": "Quests Engine"
            })

        if not documents:
            return []

        # 2. Tokenize docs and calculate TF-IDF
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return documents[:limit]

        # Calculate TF vectors
        query_tf = {}
        for t in query_tokens:
            query_tf[t] = query_tf.get(t, 0) + 1

        ranked_docs = []
        for doc in documents:
            doc_tokens = self._tokenize(doc["text"])
            doc_tf = {}
            for t in doc_tokens:
                doc_tf[t] = doc_tf.get(t, 0) + 1
                
            similarity = self._calculate_cosine_similarity(query_tf, doc_tf)
            ranked_docs.append((similarity, doc))

        # Sort by similarity score descending
        ranked_docs.sort(key=lambda x: x[0], reverse=True)
        
        # Extract matching docs above threshold (similarity > 0)
        results = [doc for score, doc in ranked_docs if score > 0.0]
        
        # Fallback to latest items if no exact similarity matches
        if not results:
            results = [doc for score, doc in ranked_docs][:limit]
            
        return results[:limit]

# Reusable global instance
rag_engine = RAGEngine()
