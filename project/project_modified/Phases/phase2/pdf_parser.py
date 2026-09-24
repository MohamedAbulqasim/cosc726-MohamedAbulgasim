"""
phase_2_ingestion_rag/pdf_parser.py
Curriculum Ingestion Engine for PDF and TXT syllabus documents.
Extracts clean, structured text, sections, and metadata using pypdf.
Author: Mohammad Abulgasim | Supervisor: Dr. Fakhreldeen Saeed
Academic Context: COSC726 Agentic AI
"""

import os
import re
from typing import Dict, Any, List, Optional
from pypdf import PdfReader

class ExtractedDocument:
    def __init__(self, raw_text: str, pages: List[Dict[str, Any]], filename: str):
        self.raw_text = raw_text
        self.pages = pages  # List of {"page_number": int, "text": str}
        self.filename = filename

class SyllabusParser:
    """
    Ingests unstructured curriculum documents (PDF or TXT) and parses them
    into page-indexed, normalized text streams ready for Parent-Child chunking.
    """

    @classmethod
    def parse_file(cls, file_path: str) -> ExtractedDocument:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Syllabus file not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            return cls._parse_pdf(file_path)
        elif ext in [".txt", ".md"]:
            return cls._parse_txt(file_path)
        else:
            raise ValueError(f"Unsupported file extension: {ext}. Only .pdf and .txt are supported.")

    @classmethod
    def _parse_pdf(cls, file_path: str) -> ExtractedDocument:
        reader = PdfReader(file_path)
        pages = []
        full_text_list = []

        for page_idx, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            clean_page_text = cls._clean_text(page_text)
            pages.append({
                "page_number": page_idx + 1,
                "text": clean_page_text
            })
            full_text_list.append(clean_page_text)

        full_raw_text = "\n\n".join(full_text_list)
        return ExtractedDocument(
            raw_text=full_raw_text,
            pages=pages,
            filename=os.path.basename(file_path)
        )

    @classmethod
    def _parse_txt(cls, file_path: str) -> ExtractedDocument:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            raw_content = f.read()

        clean_text = cls._clean_text(raw_content)
        pages = [{"page_number": 1, "text": clean_text}]
        return ExtractedDocument(
            raw_text=clean_text,
            pages=pages,
            filename=os.path.basename(file_path)
        )

    @staticmethod
    def _clean_text(text: str) -> str:
        # Normalize carriage returns and non-breaking spaces
        text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\u00a0", " ")
        # Collapse multiple blank lines into two
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Strip trailing whitespaces per line
        lines = [line.strip() for line in text.split("\n")]
        return "\n".join(lines).strip()

    @staticmethod
    def extract_metadata_heuristics(text: str, filename: str = "") -> Dict[str, Any]:
        """
        Extracts foundational scheduling constraints, language, and course identity from raw syllabus text:
        - Language (auto-detected 'ar' or 'en')
        - Practical lab presence (has_lab = True/False) and practical domain (python, sql, bash, etc.)
        - Course title and code
        - Target weeks and contact hour allocation
        """
        # 1. Language Detection
        arabic_chars = len(re.findall(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]", text))
        total_alpha = len(re.findall(r"[A-Za-z\u0600-\u06FF]", text))
        is_arabic = (arabic_chars / max(total_alpha, 1)) > 0.25

        metadata = {
            "title": "مقرر دراسي أكاديمي" if is_arabic else "Academic Course Curriculum",
            "course_code": "COURSE",
            "language": "ar" if is_arabic else "en",
            "has_lab": True,
            "practical_domain": "python",
            "weeks": 4,
            "total_hours": 32.0,
            "lecture_hours": 16.0,
            "lab_hours": 16.0,
            "discovered_topics": []
        }

        # 2. Course Title Heuristic
        title_found = None
        # Pattern A: Explicit label (Arabic or English)
        title_match = re.search(r"(?:COURSE\s+TITLE|COURSE\s+NAME|COURSE\s+SYLLABUS|SYLLABUS\s+FOR|TITLE|SUBJECT|اسم المقرر|عنوان المقرر|مقرر|المقرر|مادة|المادة):\s*(.+)", text, re.IGNORECASE)
        if title_match:
            candidate = title_match.group(1).split("\n")[0].strip()
            candidate = re.sub(r"^[-:\| ]+|[-:\| ]+$", "", candidate)
            if len(candidate) > 3:
                title_found = candidate

        # Pattern B: Inspect first non-empty lines
        if not title_found:
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            for line in lines[:8]:
                if re.search(r"(?:department|university|college|semester|academic term|fall|spring|summer|page \d+|جامعة|كلية|قسم|فصل دراسي)", line, re.IGNORECASE):
                    continue
                if 4 <= len(line) <= 85 and not line.startswith("[") and not line.startswith("-"):
                    title_found = line
                    break

        # Pattern C: Fallback to filename
        if not title_found and filename:
            clean_fn = os.path.splitext(os.path.basename(filename))[0]
            clean_fn = re.sub(r"[_\-]+", " ", clean_fn).title()
            title_found = clean_fn

        if title_found:
            metadata["title"] = title_found

        # 3. Course Code Heuristic (e.g. COSC726, CS101, SE402, IT-305, عال 101, نل 202)
        code_match = re.search(r"\b([A-Z]{2,6}\s*[-_]?\s*\d{2,4}[A-Z]?)\b", text)
        if code_match:
            metadata["course_code"] = code_match.group(1).replace(" ", "").upper()
        else:
            ar_code = re.search(r"((?:عال|نل|هس|قعد|تقن)\s*\d{2,4})", text)
            if ar_code:
                metadata["course_code"] = ar_code.group(1).strip()
            else:
                code_in_title = re.search(r"\b([A-Z]{2,6}\s*[-_]?\s*\d{2,4}[A-Z]?)\b", metadata["title"])
                if code_in_title:
                    metadata["course_code"] = code_in_title.group(1).replace(" ", "").upper()

        # 4. Weeks heuristic
        weeks_match = re.search(r"(\d+)\s*(?:instructional\s*)?(?:weeks|أسابيع|أسبوع)", text, re.IGNORECASE)
        if weeks_match:
            metadata["weeks"] = int(weeks_match.group(1))

        # 5. Total hours heuristic
        hours_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:total\s*)?(?:contact\s*)?(?:hours|ساعات|ساعة)", text, re.IGNORECASE)
        if hours_match:
            metadata["total_hours"] = float(hours_match.group(1))

        # 6. Practical / Lab presence and hours
        has_lab_keywords = bool(re.search(r"(?:lab|laboratory|practical|hands-on|عملي|مختبر|معمل|تطبيقي)", text, re.IGNORECASE))
        zero_lab_match = bool(re.search(r"(?:lab(?:oratory)?\s*hours?:\s*0|0\s*(?:ساعات\s*)?عملي|ساعات العملي:\s*0|نظري فقط)", text, re.IGNORECASE))

        lec_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:lecture\s*)?(?:hours|ساعات محاضرة|ساعات نظري)", text, re.IGNORECASE)
        lab_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:lab(?:oratory)?\s*)?(?:hours|ساعات عملي|ساعات مختبر)", text, re.IGNORECASE)

        if zero_lab_match or not has_lab_keywords:
            metadata["has_lab"] = False
            metadata["lab_hours"] = 0.0
            metadata["lecture_hours"] = metadata["total_hours"]
            metadata["practical_domain"] = "none"
        else:
            metadata["has_lab"] = True
            if lec_match and lab_match:
                metadata["lecture_hours"] = float(lec_match.group(1))
                metadata["lab_hours"] = float(lab_match.group(1))
            else:
                half = metadata["total_hours"] / 2.0
                metadata["lecture_hours"] = half
                metadata["lab_hours"] = half

            # 7. Practical Domain Detection
            if re.search(r"\b(sql|database|databases|queries|erd|قواعد البيانات|استعلامات)\b", text, re.IGNORECASE):
                metadata["practical_domain"] = "sql"
            elif re.search(r"\b(bash|shell|linux|terminal|أوامر لينكس|سطر الأوامر)\b", text, re.IGNORECASE):
                metadata["practical_domain"] = "bash"
            elif re.search(r"\b(c\+\+|cpp|c programming|برمجة سي)\b", text, re.IGNORECASE):
                metadata["practical_domain"] = "cpp"
            elif re.search(r"\b(java|oop|object-oriented|جافا)\b", text, re.IGNORECASE) and "javascript" not in text.lower():
                metadata["practical_domain"] = "java"
            elif re.search(r"\b(html|css|javascript|web development|تطوير الويب|واجهات)\b", text, re.IGNORECASE):
                metadata["practical_domain"] = "web"
            elif re.search(r"\b(case study|دراسة حالة|دراسة حالات|تحليل واقعي|إدارة|تسويق|قانون|إداري)\b", text, re.IGNORECASE):
                metadata["practical_domain"] = "case_study"
            else:
                metadata["practical_domain"] = "python"

        # 8. Discover weekly topics from text
        week_matches = re.findall(r"(?:WEEK|MODULE|UNIT|CHAPTER|الأسبوع|الوحدة|المحور)\s*\d+[:\- ]+([^\n\r]+)", text, re.IGNORECASE)
        if week_matches:
            metadata["discovered_topics"] = [m.strip() for m in week_matches if len(m.strip()) > 3]

        return metadata
