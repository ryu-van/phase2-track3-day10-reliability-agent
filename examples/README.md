# Cache Timing Examples

## Quick Demo

Run the interactive demo to see cache timing metrics in action:

```bash
python examples/cache_timing_demo.py
```

## Output

The demo will show:

1. **Cache Population** - Loading sample queries into cache
2. **Cache Lookups** - Mix of hits and misses
3. **Timing Statistics** - Comprehensive performance metrics
4. **Performance Insights** - Automatic analysis
5. **JSON Export** - Metrics saved to file

## Example Output

```
📊 Cache Timing Statistics:
======================================================================

📈 Operation Counts:
  Total GET operations:  8
  Total SET operations:  5
  Cache hits:            7
  Cache misses:          1
  Hit rate:              87.5%

⏱️  Latency Metrics (milliseconds):
  Average GET latency:   0.891 ms
  Average SET latency:   0.106 ms
  Average HIT latency:   0.961 ms
  Average MISS latency:  0.395 ms
  P95 GET latency:       2.383 ms
```

## Code Usage

```python
from reliability_lab.cache import ResponseCache

# Create cache with timing
cache = ResponseCache(ttl_seconds=60, similarity_threshold=0.6)

# Use cache normally
cache.set("query", "response")
result, score = cache.get("query")

# Get comprehensive timing stats
stats = cache.get_timing_stats()

# Access specific metrics
print(f"Average latency: {stats['avg_get_latency_ms']:.3f} ms")
print(f"Hit rate: {stats['cache_hits'] / stats['total_get_ops'] * 100:.1f}%")
print(f"P95 latency: {stats['p95_get_latency_ms']:.3f} ms")
```

## Available Metrics

- `avg_get_latency_ms` - Average GET operation time
- `avg_set_latency_ms` - Average SET operation time  
- `avg_hit_latency_ms` - Average time for cache hits
- `avg_miss_latency_ms` - Average time for cache misses
- `p95_get_latency_ms` - 95th percentile GET latency
- `total_get_ops` - Total GET operations count
- `total_set_ops` - Total SET operations count
- `cache_hits` - Number of successful hits
- `cache_misses` - Number of misses

## Documentation

See full documentation: [docs/CACHE_TIMING.md](../docs/CACHE_TIMING.md)
