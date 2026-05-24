import logging
import os
from typing import List, Dict

import pandas as pd
import pypdf

logger = logging.getLogger(__name__)


class DocumentLoader:
    def load_csv(self, filepath: str) -> List[str]:
        """Load CSV with 'question' and 'answer' columns."""
        try:
            df = pd.read_csv(filepath)
            if "question" not in df.columns or "answer" not in df.columns:
                raise ValueError("CSV must have 'question' and 'answer' columns")
            docs = []
            for _, row in df.iterrows():
                text = f"Q: {row['question']}\nA: {row['answer']}"
                docs.append(text)
            logger.info("Loaded %d documents from CSV: %s", len(docs), filepath)
            return docs
        except FileNotFoundError:
            logger.error("CSV file not found: %s", filepath)
            return []
        except Exception as e:
            logger.error("Failed to load CSV %s: %s", filepath, e)
            return []

    def load_pdf(self, filepath: str) -> List[str]:
        """Load PDF and return list of text chunks."""
        try:
            reader = pypdf.PdfReader(filepath)
            chunks = []
            for page in reader.pages:
                text = page.extract_text()
                if text and text.strip():
                    chunks.extend(self.chunk_text(text))
            logger.info("Loaded %d chunks from PDF: %s", len(chunks), filepath)
            return chunks
        except FileNotFoundError:
            logger.error("PDF file not found: %s", filepath)
            return []
        except Exception as e:
            logger.error("Failed to load PDF %s: %s", filepath, e)
            return []

    def load_text(self, filepath: str) -> List[str]:
        """Load plain text file and return list of strings."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            chunks = self.chunk_text(content)
            logger.info("Loaded %d chunks from text file: %s", len(chunks), filepath)
            return chunks
        except FileNotFoundError:
            logger.error("Text file not found: %s", filepath)
            return []
        except Exception as e:
            logger.error("Failed to load text file %s: %s", filepath, e)
            return []

    def load_from_dict(self, data: List[Dict]) -> List[str]:
        """Accept list of {question, answer} dicts."""
        docs = []
        for item in data:
            q = item.get("question", "")
            a = item.get("answer", "")
            if q and a:
                docs.append(f"Q: {q}\nA: {a}")
        logger.info("Loaded %d documents from dict", len(docs))
        return docs

    def chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks."""
        if not text or not text.strip():
            return []
        words = text.split()
        chunks = []
        start = 0
        while start < len(words):
            end = start + chunk_size
            chunk = " ".join(words[start:end])
            chunks.append(chunk)
            start += chunk_size - overlap
        return chunks
