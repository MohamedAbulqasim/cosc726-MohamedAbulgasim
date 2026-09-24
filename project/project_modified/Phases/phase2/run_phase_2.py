"""
phase_2_ingestion_rag/run_phase_2.py
Standalone test and verification runner for Phase 2: Ingestion & Parent-Child RAG.
Tests:
  1. PDF parsing and TXT parsing via SyllabusParser
  2. Metadata heuristics extraction (weeks, hours, course title)
  3. Parent-Child chunking (~700 char parents, ~200 char children)
  4. SyllabusKnowledgeBase indexing & BM25 retrieval
  5. Parent context dereferencing and citation registry validation
"""

import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from phase_2_ingestion_rag.pdf_parser import SyllabusParser
from phase_2_ingestion_rag.parent_child_chunker import ParentChildChunker
from phase_2_ingestion_rag.knowledge_base import SyllabusKnowledgeBase

def run_tests():
    print("=" * 75)
    print("RUNNING PHASE 2 VERIFICATION: INGESTION & PARENT-CHILD RAG")
    print("=" * 75)

    sample_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sample_curriculum"))
    pdf_path = os.path.join(sample_dir, "sample_syllabus.pdf")
    txt_path = os.path.join(sample_dir, "sample_syllabus.txt")

    # 1. Test Ingestion & PDF Parser
    print("\n[TEST 1] Testing PDF and TXT Ingestion...")
    doc_pdf = SyllabusParser.parse_file(pdf_path)
    print(f"  -> Ingested PDF: '{doc_pdf.filename}' ({len(doc_pdf.pages)} pages, {len(doc_pdf.raw_text)} chars).")
    assert len(doc_pdf.raw_text) > 500, "PDF text extraction yielded insufficient content."

    doc_txt = SyllabusParser.parse_file(txt_path)
    print(f"  -> Ingested TXT: '{doc_txt.filename}' ({len(doc_txt.raw_text)} chars).")
    assert len(doc_txt.raw_text) > 500, "TXT text extraction yielded insufficient content."

    # 2. Test Metadata Extraction Heuristics
    print("\n[TEST 2] Testing Metadata Extraction Heuristics...")
    meta = SyllabusParser.extract_metadata_heuristics(doc_pdf.raw_text)
    print(f"  Extracted Metadata: Title='{meta['title']}', Weeks={meta['weeks']}, TotalHours={meta['total_hours']}, LectureHours={meta['lecture_hours']}, LabHours={meta['lab_hours']}")
    assert meta["weeks"] == 4, f"Expected 4 weeks, got {meta['weeks']}"
    assert meta["total_hours"] == 32.0, f"Expected 32.0 hours, got {meta['total_hours']}"
    print("  -> Metadata extraction heuristics PASSED.")

    # 3. Test Parent-Child Chunking Engine
    print("\n[TEST 3] Testing Parent-Child Chunking (~700 / ~200 characters)...")
    chunker = ParentChildChunker(parent_chunk_size=700, parent_overlap=100, child_chunk_size=200, child_overlap=40)
    parents, children = chunker.chunk_document(doc_pdf)

    print(f"  -> Generated {len(parents)} Parent chunks and {len(children)} Child chunks.")
    assert len(parents) > 0, "No parent chunks generated."
    assert len(children) > len(parents), "Expected more child chunks than parent chunks."

    avg_p_len = sum(p.char_length for p in parents) / len(parents)
    avg_c_len = sum(c.char_length for c in children) / len(children)
    print(f"  -> Average Parent Length: {avg_p_len:.1f} chars | Average Child Length: {avg_c_len:.1f} chars")
    assert 300 < avg_p_len < 900, f"Parent chunk average size {avg_p_len} out of expected bounds."
    assert 100 < avg_c_len < 300, f"Child chunk average size {avg_c_len} out of expected bounds."

    # 4. Test SyllabusKnowledgeBase Indexing & Retrieval
    print("\n[TEST 4] Testing KnowledgeBase Retrieval with Parent Dereferencing...")
    kb = SyllabusKnowledgeBase()
    kb.index_curriculum(parents, children)

    test_queries = [
        "Parent-Child chunking mechanics and context preservation",
        "Separation of concerns between Model, Harness, and Agent",
        "Deterministic tool calling with Pydantic"
    ]

    for q in test_queries:
        print(f"\n  Query: '{q}'")
        results = kb.retrieve(q, top_k=2)
        assert len(results) > 0, f"Retrieval failed to find matches for query: {q}"
        top = results[0]
        print(f"    Matched Child:  {top.child_chunk.chunk_id} (Score: {top.relevance_score:.3f})")
        print(f"    Dereferenced Parent: {top.parent_chunk.chunk_id} [{top.parent_chunk.section_name}]")
        print(f"    Parent Context Preview: {top.parent_chunk.text[:140]}...")
        assert top.parent_chunk.chunk_id == top.child_chunk.parent_id, "Parent ID dereference mismatch!"

    # 5. Test Citation Registry & Gate 3 Grounding Support
    print("\n[TEST 5] Testing Citation Registry for Gate 3 Provenance Verification...")
    first_parent_id = parents[0].chunk_id
    assert kb.is_valid_citation(first_parent_id), f"Parent ID {first_parent_id} not recognized in registry!"
    assert not kb.is_valid_citation("PARENT-999"), "Unknown parent ID falsely recognized!"
    print(f"  -> Citation Registry verified: {len(kb.citation_registry)} registered citations.")

    print("\n" + "=" * 75)
    print("ALL PHASE 2 INGESTION & PARENT-CHILD RAG TESTS VERIFIED SUCCESSFULLY!")
    print("=" * 75)
    return True

if __name__ == "__main__":
    success = run_tests()
    if not success:
        sys.exit(1)
