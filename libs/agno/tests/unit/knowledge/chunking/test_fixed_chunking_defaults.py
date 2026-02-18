"""
BUG #4540 regression guards.

Root cause 1: FixedSizeChunking default chunk_size was 100 instead of 5000
in agno v2.0.0, causing 100x more chunks and API calls. Fixed Sep 2025.

Root cause 2: Batch embedding disabled by default — each chunk triggers a
separate HTTP embedding request. Batch embedding exists but enable_batch=False.
"""
from agno.knowledge.chunking.fixed import FixedSizeChunking
from agno.knowledge.document.base import Document
from agno.knowledge.embedder.base import Embedder
from agno.knowledge.reader.text_reader import TextReader


def test_default_chunk_size_is_5000():
    """BUG #4540(a): default chunk_size regressed to 100 in v2.0.0."""
    chunking = FixedSizeChunking()
    assert chunking.chunk_size == 5000


def test_large_document_produces_reasonable_chunk_count():
    """
    BUG #4540(a): A 10K char document should produce ~2 chunks at 5000 default,
    not ~100 chunks (which happened when chunk_size was 100).
    """
    chunking = FixedSizeChunking()
    content = "word " * 2000  # ~10K chars
    doc = Document(name="test", content=content)

    chunks = chunking.chunk(doc)

    # At chunk_size=5000: should be ~2-3 chunks
    # At chunk_size=100 (the regressed value): would be ~100 chunks
    assert len(chunks) <= 5, f"Expected ~2-3 chunks, got {len(chunks)} (possible chunk_size regression)"
    assert len(chunks) >= 2, f"Expected at least 2 chunks for 10K chars, got {len(chunks)}"


def test_text_reader_default_chunking_uses_5000():
    """
    BUG #4540(a): TextReader (the default reader for most file types) should
    use FixedSizeChunking with chunk_size=5000 by default.
    """
    reader = TextReader()
    assert reader.chunk is True
    assert reader.chunk_size == 5000
    assert isinstance(reader.chunking_strategy, FixedSizeChunking)
    assert reader.chunking_strategy.chunk_size == 5000


def test_batch_embedding_disabled_by_default():
    """
    BUG #4540(b): Batch embedding is OFF by default, meaning each chunk
    triggers a separate HTTP embedding call. This is the remaining perf issue.

    This test documents the current behavior. When enable_batch defaults to
    True in a future release, update this test accordingly.
    """
    embedder = Embedder()
    # This PASSES because enable_batch is currently False.
    # Flip the assertion when the default changes to True.
    assert embedder.enable_batch is False, (
        "enable_batch is still False by default — each chunk makes a separate "
        "embedding API call. Consider enabling by default for better perf."
    )
