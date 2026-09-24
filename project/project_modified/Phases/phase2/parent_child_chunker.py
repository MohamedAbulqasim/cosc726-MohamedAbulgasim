"""
phase_2_ingestion_rag/parent_child_chunker.py
Parent-Child Chunking Engine.
Implements the dual-granularity RAG strategy specified in the project proposal:
- Indexes small child segments (~200 characters) for high-precision vector/lexical search
- Dereferences and returns comprehensive parent containers (~700 characters) for context grounding
Author: Mohammad Abulgasim | Supervisor: Dr. Fakhreldeen Saeed
Academic Context: COSC726 Agentic AI
"""

import re
from typing import List, Dict, Tuple, Optional
from phase_1_architecture_contracts.contracts import SyllabusChunk
from phase_2_ingestion_rag.pdf_parser import ExtractedDocument

class ParentChildChunker:
    """
    Splits text streams into dual-granularity chunks:
      - Parent chunks: ~700 characters (context containers)
      - Child chunks: ~200 characters (search index targets)
    """

    def __init__(
        self,
        parent_chunk_size: int = 700,
        parent_overlap: int = 100,
        child_chunk_size: int = 200,
        child_overlap: int = 40
    ):
        self.parent_chunk_size = parent_chunk_size
        self.parent_overlap = parent_overlap
        self.child_chunk_size = child_chunk_size
        self.child_overlap = child_overlap

    def chunk_document(self, doc: ExtractedDocument) -> Tuple[List[SyllabusChunk], List[SyllabusChunk]]:
        """
        Processes an ExtractedDocument and returns:
          - parents: List of SyllabusChunk (chunk_type="parent")
          - children: List of SyllabusChunk (chunk_type="child", referencing parent_id)
        """
        all_parents: List[SyllabusChunk] = []
        all_children: List[SyllabusChunk] = []
        parent_counter = 1

        for page in doc.pages:
            page_num = page["page_number"]
            page_text = page["text"]

            # Split page text into parent blocks (~700 chars)
            parent_blocks = self._split_into_windows(
                text=page_text,
                window_size=self.parent_chunk_size,
                overlap=self.parent_overlap
            )

            for p_text in parent_blocks:
                if len(p_text.strip()) < 30:
                    continue

                parent_id = f"PARENT-{parent_counter:03d}"
                section_name = self._infer_section(p_text)

                parent_chunk = SyllabusChunk(
                    chunk_id=parent_id,
                    parent_id=None,
                    chunk_type="parent",
                    text=p_text.strip(),
                    section_name=section_name,
                    page_number=page_num,
                    char_length=len(p_text.strip())
                )
                all_parents.append(parent_chunk)

                # Now split this parent into child chunks (~200 chars)
                child_blocks = self._split_into_windows(
                    text=p_text,
                    window_size=self.child_chunk_size,
                    overlap=self.child_overlap
                )

                for c_idx, c_text in enumerate(child_blocks):
                    if len(c_text.strip()) < 15:
                        continue
                    child_id = f"CHILD-{parent_counter:03d}-{c_idx+1:02d}"
                    child_chunk = SyllabusChunk(
                        chunk_id=child_id,
                        parent_id=parent_id,
                        chunk_type="child",
                        text=c_text.strip(),
                        section_name=section_name,
                        page_number=page_num,
                        char_length=len(c_text.strip())
                    )
                    all_children.append(child_chunk)

                parent_counter += 1

        return all_parents, all_children

    def _split_into_windows(self, text: str, window_size: int, overlap: int) -> List[str]:
        """
        Paragraph-aware and sliding window text splitter with sentence/punctuation boundary alignment.
        Preserves natural section and paragraph boundaries whenever possible.
        """
        if len(text) <= window_size:
            return [text.strip()] if text.strip() else []

        raw_paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        if len(raw_paras) <= 1 and "\n" in text:
            raw_paras = [p.strip() for p in text.split("\n") if p.strip()]

        chunks = []
        current_chunk = []
        current_len = 0

        for p in raw_paras:
            p_len = len(p)
            if p_len > window_size:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                    current_chunk = []
                    current_len = 0

                sub_start = 0
                while sub_start < len(p):
                    sub_end = min(sub_start + window_size, len(p))
                    if sub_end < len(p):
                        m = re.search(r"[\n\.\?!;]\s*", p[sub_end - 60:sub_end + 30])
                        if m:
                            sub_end = (sub_end - 60) + m.end()
                    sub_text = p[sub_start:sub_end].strip()
                    if sub_text:
                        chunks.append(sub_text)
                    sub_start += (window_size - overlap)
                    if sub_end >= len(p):
                        break
                continue

            if current_len + p_len + (2 if current_chunk else 0) <= window_size:
                current_chunk.append(p)
                current_len += p_len + (2 if current_chunk else 0)
            else:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                current_chunk = [p]
                current_len = p_len

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def _infer_section(self, text: str) -> str:
        """
        Infers the active syllabus section from heading markers or content keywords (supporting both EN and AR).
        """
        w_match = re.search(
            r"((?:WEEK|MODULE|UNIT|CHAPTER|الأسبوع|الوحدة|الفصل|المحاضرة)\s*(?:\d+|الأول|الثاني|الثالث|الرابع|الخامس|السادس|السابع|الثامن|التاسع|العاشر)[\s:\-]*[^\n\r]*)",
            text,
            re.IGNORECASE
        )
        if w_match:
            cand = w_match.group(1).split("- Lecture")[0].split("- موضوعات")[0].split("|")[0].strip()
            if len(cand) > 45:
                cand = cand[:42] + "..."
            return cand
        match = re.search(
            r"(\[SECTION[^\]]+\]|LEARNING OUTCOMES|COURSE OVERVIEW|القسم\s*\d+[:\- ]*[^\n\r]*|توصيف المقرر|أهداف المقرر)",
            text,
            re.IGNORECASE
        )
        if match:
            return match.group(1).strip()
        return "Curriculum Core"
