"""
Stage 2 of the pipeline: splitting documents into chunks.

`split_documents` merges each document's paragraphs into a chunk up to
CHUNK_SIZE, only splitting where a paragraph break already is one. See its
docstring for why that fits campus_life specifically.

`fallback_split` is the starter's original: fixed-size character windows with
a fixed overlap, blind to sentence or paragraph boundaries. It's kept as the
thing to fall back to (and to compare against) if the paragraph-merge
strategy above ever gets stuck on a corpus it doesn't fit.
"""

from dataclasses import dataclass

import config
from ingest import Document


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Split documents into chunks, merging whole paragraphs up to CHUNK_SIZE.

    campus_life is 88 short, single-topic notes — the longest is 563
    characters (checked with `wc -c corpora/campus_life/documents/*.txt`),
    every idea in a post lives in one or two paragraphs, and there's no
    internal section structure to split on. Cutting one of these on a
    character count risks slicing a sentence in half for no benefit, since
    almost none of them are long enough to need splitting at all.

    So the rule is: merge a document's paragraphs into a chunk as long as the
    result still fits under CHUNK_SIZE, and start a new chunk when the next
    paragraph would push it over. CHUNK_SIZE (1000) is set above the longest
    document in this corpus on purpose, so in practice every post here stays
    one chunk — a post never gets split unless it or a paragraph is genuinely
    too long to fit. The one paragraph that IS too long on its own falls back
    to the fixed-window split with overlap, so a single run-on paragraph
    still doesn't turn into one giant chunk.
    """
    chunk_size = config.CHUNK_SIZE
    overlap = config.CHUNK_OVERLAP
    chunks: list[Chunk] = []

    for doc in documents:
        paragraphs = [p.strip() for p in doc.text.split("\n\n") if p.strip()]
        index = 0
        current = ""

        def flush(piece: str) -> None:
            nonlocal index
            piece = piece.strip()
            if not piece:
                return
            chunks.append(
                Chunk(
                    text=piece,
                    source=doc.source,
                    index=index,
                    produced_by="chunker.py::split_documents",
                )
            )
            index += 1

        for para in paragraphs:
            if len(para) > chunk_size:
                # A single paragraph too long to keep whole. Flush whatever
                # was building, then window this one paragraph on its own.
                flush(current)
                current = ""
                start = 0
                while start < len(para):
                    flush(para[start : start + chunk_size])
                    start += chunk_size - overlap
                continue

            candidate = f"{current}\n\n{para}" if current else para
            if len(candidate) <= chunk_size:
                current = candidate
            else:
                flush(current)
                current = para

        flush(current)

    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
