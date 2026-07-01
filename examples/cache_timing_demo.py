#!/usr/bin/env python3
"""
Cache Timing Metrics Demo

This script demonstrates the cache timing instrumentation added to track:
- get() and set() operation latency
- Cache hit vs miss latency
- P95 latency for performance monitoring
"""

import json
import time
from reliability_lab.cache import ResponseCache


def main():
    print("=" * 70)
    print("Cache Timing Metrics Demo")
    print("=" * 70)
    print()
    
    # Create cache
    cache = ResponseCache(ttl_seconds=60, similarity_threshold=0.6)
    
    # Simulate realistic workload
    print("📝 Populating cache with sample queries...")
    queries = [
        ("What is the capital of France?", "Paris is the capital of France."),
        ("How do I make a chocolate cake?", "Mix flour, eggs, sugar, and cocoa powder..."),
        ("What is the weather in New York?", "Currently 72°F and sunny in New York."),
        ("Tell me about Python programming", "Python is a high-level programming language..."),
        ("Best restaurants in Tokyo", "Top restaurants in Tokyo include Sukiyabashi Jiro..."),
    ]
    
    for query, response in queries:
        cache.set(query, response)
        time.sleep(0.01)  # Simulate realistic delays
    
    print(f"✅ Cached {len(queries)} responses\n")
    
    # Simulate cache lookups (hits and misses)
    print("🔍 Performing cache lookups...")
    test_queries = [
        ("What is the capital of France?", "exact hit"),
        ("What is capital of France", "similar hit"),
        ("How do I bake a chocolate cake?", "similar hit"),
        ("What is the weather in London?", "miss"),
        ("Tell me about Java programming", "miss"),
        ("What is the capital of France?", "exact hit again"),
        ("Best restaurants Tokyo", "similar hit"),
        ("What is quantum computing?", "miss"),
    ]
    
    for query, expected in test_queries:
        result, score = cache.get(query)
        hit_status = "✅ HIT" if result else "❌ MISS"
        print(f"  {hit_status} [{expected:15s}] score={score:.3f} | {query[:40]}")
        time.sleep(0.005)  # Simulate processing
    
    print()
    
    # Get timing statistics
    print("📊 Cache Timing Statistics:")
    print("=" * 70)
    stats = cache.get_timing_stats()
    
    print(f"\n📈 Operation Counts:")
    print(f"  Total GET operations:  {stats['total_get_ops']}")
    print(f"  Total SET operations:  {stats['total_set_ops']}")
    print(f"  Cache hits:            {stats['cache_hits']}")
    print(f"  Cache misses:          {stats['cache_misses']}")
    print(f"  Hit rate:              {stats['cache_hits'] / stats['total_get_ops'] * 100:.1f}%")
    
    print(f"\n⏱️  Latency Metrics (milliseconds):")
    print(f"  Average GET latency:   {stats['avg_get_latency_ms']:.3f} ms")
    print(f"  Average SET latency:   {stats['avg_set_latency_ms']:.3f} ms")
    print(f"  Average HIT latency:   {stats['avg_hit_latency_ms']:.3f} ms")
    print(f"  Average MISS latency:  {stats['avg_miss_latency_ms']:.3f} ms")
    print(f"  P95 GET latency:       {stats['p95_get_latency_ms']:.3f} ms")
    
    # Performance insights
    print(f"\n💡 Performance Insights:")
    if stats['avg_hit_latency_ms'] < stats['avg_miss_latency_ms']:
        print(f"  ✅ Cache hits are faster than misses (expected behavior)")
        savings = stats['avg_miss_latency_ms'] - stats['avg_hit_latency_ms']
        print(f"     Average savings per hit: {savings:.3f} ms")
    else:
        print(f"  ⚠️  Cache hits are slower than misses (unexpected)")
    
    if stats['p95_get_latency_ms'] > stats['avg_get_latency_ms'] * 2:
        print(f"  ⚠️  P95 latency is high - some queries are much slower than average")
    else:
        print(f"  ✅ P95 latency is reasonable - consistent performance")
    
    # Export to JSON
    print(f"\n💾 Exporting metrics to JSON...")
    with open("cache_timing_metrics.json", "w") as f:
        json.dump(stats, f, indent=2)
    print(f"  Saved to: cache_timing_metrics.json")
    
    print("\n" + "=" * 70)
    print("Demo complete! Cache timing metrics are now tracked for observability.")
    print("=" * 70)


if __name__ == "__main__":
    main()
