"""
phase_2_ingestion_rag/knowledge_base.py
SyllabusKnowledgeBase: High-precision retrieval engine with Parent-Child dereferencing.
Indexes child chunks (~200 chars) for granular semantic/lexical discovery,
and dereferences to parent containers (~700 chars) for rich, un-truncated context grounding.
Maintains citation registry for Gate 3 (Refers) verification.
Author: Mohammad Abulgasim | Supervisor: Dr. Fakhreldeen Saeed
Academic Context: COSC726 Agentic AI
"""

import math
import re
from typing import List, Dict, Set, Optional, Tuple, Any
from phase_1_architecture_contracts.contracts import SyllabusChunk

class RetrievalResult:
    def __init__(
        self,
        child_chunk: SyllabusChunk,
        parent_chunk: SyllabusChunk,
        relevance_score: float,
        citation_tag: str
    ):
        self.child_chunk = child_chunk
        self.parent_chunk = parent_chunk
        self.relevance_score = relevance_score
        self.citation_tag = citation_tag

    def to_dict(self) -> Dict[str, Any]:
        return {
            "citation_tag": self.citation_tag,
            "relevance_score": round(self.relevance_score, 4),
            "matched_child_id": self.child_chunk.chunk_id,
            "parent_id": self.parent_chunk.chunk_id,
            "section": self.parent_chunk.section_name,
            "page": self.parent_chunk.page_number,
            "grounded_context": self.parent_chunk.text
        }

class SyllabusKnowledgeBase:
    """
    In-memory Parent-Child RAG Knowledge Base with BM25/Lexical relevance scoring
    and provenance registry.
    """

    def __init__(self):
        self.parents: Dict[str, SyllabusChunk] = {}
        self.children: List[SyllabusChunk] = []
        self.citation_registry: Set[str] = set()
        self._doc_frequencies: Dict[str, int] = {}
        self._child_tokens: List[List[str]] = []

    def index_curriculum(self, parents: List[SyllabusChunk], children: List[SyllabusChunk]):
        """
        Loads and indexes parent containers and child segments.
        """
        self.parents = {p.chunk_id: p for p in parents}
        self.children = children
        self.citation_registry = set(self.parents.keys())

        # Also register any embedded reference tokens e.g. REF-W1-01, REF-W2-01
        for p in parents:
            refs = re.findall(r"REF-[A-Za-z0-9\-]+", p.text)
            for r in refs:
                self.citation_registry.add(r)

        # Build term frequencies for BM25-like scoring
        self._build_index()
        print(f"KnowledgeBase indexed: {len(self.parents)} parents, {len(self.children)} children, {len(self.citation_registry)} citation IDs.")

    def _tokenize(self, text: str) -> List[str]:
        tokens = re.findall(r"\b\w+\b", text.lower())
        stopwords = {"the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "of", "with", "is", "are", "by"}
        return [t for t in tokens if t not in stopwords and (len(t) > 1 or t.isdigit())]

    def _build_index(self):
        self._doc_frequencies = {}
        self._child_tokens = []

        for child in self.children:
            tokens = self._tokenize(child.text)
            self._child_tokens.append(tokens)
            unique_terms = set(tokens)
            for term in unique_terms:
                self._doc_frequencies[term] = self._doc_frequencies.get(term, 0) + 1

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        week_num: Optional[int] = None,
        total_weeks: Optional[int] = None
    ) -> List[RetrievalResult]:
        """
        Retrieves top_k most relevant parent containers by matching the query against child segments.
        Resolves the classical RAG trade-off by returning full parent context.
        If keyword hits are insufficient, supplements with proportional syllabus partitioning.
        """
        q_tokens = self._tokenize(query)
        scored_matches: List[Tuple[int, float]] = []

        if q_tokens and self.children:
            N = len(self.children)
            avg_len = sum(len(t) for t in self._child_tokens) / max(N, 1)
            k1 = 1.5
            b = 0.75

            for idx, doc_tokens in enumerate(self._child_tokens):
                score = 0.0
                doc_len = len(doc_tokens)
                tf_dict: Dict[str, int] = {}
                for t in doc_tokens:
                    tf_dict[t] = tf_dict.get(t, 0) + 1

                for qt in q_tokens:
                    if qt in tf_dict:
                        df = self._doc_frequencies.get(qt, 1)
                        idf = math.log((N - df + 0.5) / (df + 0.5) + 1.0)
                        tf = tf_dict[qt]
                        numerator = tf * (k1 + 1.0)
                        denominator = tf + k1 * (1.0 - b + b * (doc_len / avg_len))
                        score += idf * (numerator / denominator)

                if score > 0.0:
                    scored_matches.append((idx, score))

            scored_matches.sort(key=lambda x: x[1], reverse=True)

        results: List[RetrievalResult] = []
        seen_parents: Set[str] = set()

        # Check if week number is given or mentioned in query
        target_week = week_num
        if target_week is None:
            w_m = re.search(r"(?:WEEK|MODULE|UNIT|CHAPTER|الأسبوع|الاسبوع)\s*(\d+)", query, re.IGNORECASE)
            if w_m:
                target_week = int(w_m.group(1))

        # 1. Exact week priority matching: if a parent chunk explicitly matches the target week, include it first
        if target_week is not None and self.parents:
            arabic_week_names = ["الأول", "الثاني", "الثالث", "الرابع", "الخامس", "السادس", "السابع", "الثامن", "التاسع", "العاشر", "الحادي عشر", "الثاني عشر"]
            ar_w = arabic_week_names[target_week - 1] if target_week <= len(arabic_week_names) else str(target_week)
            parent_keys = list(self.parents.keys())
            for idx, pid in enumerate(parent_keys):
                p = self.parents[pid]
                sec_or_text = (p.section_name + " " + p.text[:400] + " " + p.text[-300:]).lower()
                patterns = [
                    rf"(?:week|module|unit|chapter)\s*{target_week}\b",
                    rf"(?:الأسبوع|الاسبوع)\s*(?:{target_week}|{ar_w})\b",
                    rf"(?:الوحدة|المحور|الفصل)\s*(?:{target_week}|{ar_w})\b"
                ]
                if any(re.search(pat, sec_or_text) for pat in patterns):
                    if p.chunk_id not in seen_parents:
                        seen_parents.add(p.chunk_id)
                        matched_child = next((c for c in self.children if c.parent_id == p.chunk_id), p)
                        results.append(RetrievalResult(
                            child_chunk=matched_child,
                            parent_chunk=p,
                            relevance_score=10.0,
                            citation_tag=f"[{p.chunk_id}|Page{p.page_number}]"
                        ))
                    # Also include next adjacent chunk if available to capture continuation
                    if idx + 1 < len(parent_keys):
                        next_p = self.parents[parent_keys[idx + 1]]
                        if next_p.chunk_id not in seen_parents and len(results) < top_k:
                            seen_parents.add(next_p.chunk_id)
                            matched_child = next((c for c in self.children if c.parent_id == next_p.chunk_id), next_p)
                            results.append(RetrievalResult(
                                child_chunk=matched_child,
                                parent_chunk=next_p,
                                relevance_score=9.0,
                                citation_tag=f"[{next_p.chunk_id}|Page{next_p.page_number}]"
                            ))
                    if len(results) >= top_k:
                        break

        # 2. Add BM25 search results
        for child_idx, score in scored_matches:
            if len(results) >= top_k:
                break
            child = self.children[child_idx]
            parent_id = child.parent_id
            if not parent_id or parent_id not in self.parents:
                continue

            if parent_id in seen_parents:
                continue
            seen_parents.add(parent_id)

            parent = self.parents[parent_id]
            citation_tag = f"[{parent_id}|Page{parent.page_number}]"

            results.append(RetrievalResult(
                child_chunk=child,
                parent_chunk=parent,
                relevance_score=score,
                citation_tag=citation_tag
            ))

        # 3. Proportional syllabus fallback: ensure every week gets its authentic portion of the syllabus
        if len(results) < top_k and self.parents:
            parent_list = list(self.parents.values())
            num_parents = len(parent_list)

            if target_week is not None and total_weeks is not None and total_weeks > 0:
                chunk_start = int((target_week - 1) * num_parents / total_weeks)
                chunk_end = max(chunk_start + 1, int(target_week * num_parents / total_weeks))
                selected_parents = parent_list[chunk_start:chunk_end]
            else:
                selected_parents = parent_list

            for p in selected_parents:
                if p.chunk_id not in seen_parents:
                    seen_parents.add(p.chunk_id)
                    matched_child = next((c for c in self.children if c.parent_id == p.chunk_id), p)
                    results.append(RetrievalResult(
                        child_chunk=matched_child,
                        parent_chunk=p,
                        relevance_score=1.0,
                        citation_tag=f"[{p.chunk_id}|Page{p.page_number}]"
                    ))
                    if len(results) >= top_k:
                        break

        return results

    def get_grounded_context_block(
        self,
        query: str,
        top_k: int = 3,
        week_num: Optional[int] = None,
        total_weeks: Optional[int] = None
    ) -> str:
        """
        Builds a formatted string containing retrieved parent context blocks with citation provenance tags.
        Guarantees non-empty authentic context if syllabus document was ingested.
        """
        results = self.retrieve(query, top_k=top_k, week_num=week_num, total_weeks=total_weeks)
        if not results:
            if self.parents:
                first_p = next(iter(self.parents.values()))
                return f"--- EVIDENCE CHUNK [{first_p.chunk_id}|Page{first_p.page_number}] (Section: {first_p.section_name}) ---\n{first_p.text}\n"
            return "No grounded context found in curriculum."

        blocks = []
        for r in results:
            blocks.append(
                f"--- EVIDENCE CHUNK {r.citation_tag} (Section: {r.parent_chunk.section_name}) ---\n"
                f"{r.parent_chunk.text}\n"
            )
        return "\n".join(blocks)

    def is_valid_citation(self, citation_id: str) -> bool:
        """
        Validates citation against the knowledge base provenance registry for Gate 3.
        """
        if citation_id in self.citation_registry:
            return True
        # Check if it matches parent ID prefix (e.g. PARENT-001)
        clean = citation_id.strip("[]")
        parts = clean.split("|")
        return parts[0] in self.citation_registry
