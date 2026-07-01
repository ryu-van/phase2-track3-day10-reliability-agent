"""
Test cache timing metrics.

These tests verify that cache operations track timing data for observability.
"""
from reliability_lab.cache import ResponseCache


def test_cache_tracks_get_timing():
    """Test that get() operations track timing."""
    cache = ResponseCache(ttl_seconds=60, similarity_threshold=0.5)
    cache.set("hello", "world")
    
    # Perform get operations
    cache.get("hello")  # Hit
    cache.get("goodbye")  # Miss
    
    stats = cache.get_timing_stats()
    
    assert stats["total_get_ops"] == 2
    assert stats["avg_get_latency_ms"] >= 0
    assert stats["p95_get_latency_ms"] >= 0


def test_cache_tracks_set_timing():
    """Test that set() operations track timing."""
    cache = ResponseCache(ttl_seconds=60, similarity_threshold=0.5)
    
    # Perform set operations
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.set("key3", "value3")
    
    stats = cache.get_timing_stats()
    
    assert stats["total_set_ops"] == 3
    assert stats["avg_set_latency_ms"] >= 0


def test_cache_separates_hit_and_miss_timing():
    """Test that cache tracks hit vs miss timing separately."""
    cache = ResponseCache(ttl_seconds=60, similarity_threshold=0.5)
    
    # Create some cache entries
    cache.set("what is the weather today", "response1")
    cache.set("goodbye world", "response2")
    
    # Perform operations
    cache.get("what is the weather today")  # Hit (exact match)
    cache.get("what is weather today")  # Hit (similar, score >= 0.5)
    cache.get("completely different query xyz")  # Miss (dissimilar)
    cache.get("another miss query abc")  # Miss
    
    stats = cache.get_timing_stats()
    
    assert stats["cache_hits"] == 2
    assert stats["cache_misses"] == 2
    assert stats["avg_hit_latency_ms"] >= 0
    assert stats["avg_miss_latency_ms"] >= 0
    assert stats["total_get_ops"] == 4


def test_cache_timing_with_privacy_queries():
    """Test that privacy queries don't pollute timing stats."""
    cache = ResponseCache(ttl_seconds=60, similarity_threshold=0.5)
    cache.set("normal query", "response")
    
    # Privacy queries should return early
    cache.get("what is my password")
    cache.get("normal query")  # Normal hit
    
    stats = cache.get_timing_stats()
    
    # Privacy query returns before timing is recorded
    assert stats["total_get_ops"] == 1  # Only the normal query
    assert stats["cache_hits"] == 1


def test_cache_timing_stats_empty_cache():
    """Test that timing stats work on empty cache."""
    cache = ResponseCache(ttl_seconds=60, similarity_threshold=0.5)
    
    stats = cache.get_timing_stats()
    
    assert stats["total_get_ops"] == 0
    assert stats["total_set_ops"] == 0
    assert stats["avg_get_latency_ms"] == 0.0
    assert stats["avg_set_latency_ms"] == 0.0
    assert stats["avg_hit_latency_ms"] == 0.0
    assert stats["avg_miss_latency_ms"] == 0.0


def test_cache_p95_latency_calculation():
    """Test that P95 latency is calculated correctly."""
    cache = ResponseCache(ttl_seconds=60, similarity_threshold=0.5)
    
    # Create entries
    for i in range(20):
        cache.set(f"query{i}", f"response{i}")
    
    # Perform many get operations
    for i in range(100):
        cache.get(f"query{i % 20}")
    
    stats = cache.get_timing_stats()
    
    assert stats["total_get_ops"] == 100
    assert stats["p95_get_latency_ms"] > 0
    # P95 should be >= average (typically)
    assert stats["p95_get_latency_ms"] >= stats["avg_get_latency_ms"] * 0.5


def test_cache_timing_reports_false_hits_as_misses():
    """Test that false hits are counted as misses in timing."""
    cache = ResponseCache(ttl_seconds=60, similarity_threshold=0.5)
    
    cache.set("revenue in 2020", "10 million")
    
    # This should be a false hit (different year)
    result, score = cache.get("revenue in 2021")
    
    stats = cache.get_timing_stats()
    
    assert result is None  # False hit returns None
    assert score >= cache.similarity_threshold  # Score was high
    assert stats["cache_misses"] == 1  # Should count as miss
    assert stats["cache_hits"] == 0
    assert len(cache.false_hit_log) == 1
