# Cache Timing Metrics

## Overview

Cache timing instrumentation has been added to both `ResponseCache` and `SharedRedisCache` to provide observability into cache performance. This enables monitoring of cache operation latency and helps identify performance bottlenecks.

## Features

### Tracked Metrics

Both cache implementations now track:

1. **Operation Latency**
   - `get_latency_ms`: Latency for all get() operations
   - `set_latency_ms`: Latency for all set() operations

2. **Hit/Miss Timing**
   - `hit_latency_ms`: Latency when cache returns a result
   - `miss_latency_ms`: Latency when cache has no match

3. **Aggregate Statistics** (via `get_timing_stats()`)
   - Average GET/SET latency
   - Average HIT/MISS latency
   - P95 GET latency
   - Total operation counts

## Usage

### Basic Usage

```python
from reliability_lab.cache import ResponseCache

# Create cache
cache = ResponseCache(ttl_seconds=60, similarity_threshold=0.6)

# Use cache normally
cache.set("query", "response")
result, score = cache.get("query")

# Get timing statistics
stats = cache.get_timing_stats()
print(f"Average GET latency: {stats['avg_get_latency_ms']:.3f} ms")
print(f"Cache hit rate: {stats['cache_hits'] / stats['total_get_ops'] * 100:.1f}%")
```

### Statistics Dictionary

The `get_timing_stats()` method returns:

```python
{
    "avg_get_latency_ms": 0.891,      # Average get() operation latency
    "avg_set_latency_ms": 0.106,      # Average set() operation latency
    "avg_hit_latency_ms": 0.961,      # Average latency for cache hits
    "avg_miss_latency_ms": 0.395,     # Average latency for cache misses
    "p95_get_latency_ms": 2.383,      # 95th percentile get latency
    "total_get_ops": 8,                # Total get() calls
    "total_set_ops": 5,                # Total set() calls
    "cache_hits": 7,                   # Number of cache hits
    "cache_misses": 1                  # Number of cache misses
}
```

## Implementation Details

### Timing Measurement

- Uses `time.perf_counter()` for high-resolution timing
- Timing starts at function entry
- Records latency before function returns
- Privacy queries bypass timing (return early)

### Hit vs Miss Classification

- **Cache Hit**: Result found with score >= similarity_threshold
- **Cache Miss**: No result, or false hit detected
- **False Hits**: Counted as misses (correct behavior)

### Performance Impact

The timing instrumentation has minimal overhead:
- Two `time.perf_counter()` calls per operation
- Appending float to list (amortized O(1))
- No blocking operations
- Statistics computed on-demand

## Use Cases

### 1. Performance Monitoring

Monitor cache performance in production:

```python
stats = cache.get_timing_stats()

# Alert if P95 latency exceeds threshold
if stats['p95_get_latency_ms'] > 100:
    alert("Cache P95 latency too high")

# Alert if cache hit rate drops
hit_rate = stats['cache_hits'] / stats['total_get_ops']
if hit_rate < 0.5:
    alert("Cache hit rate below 50%")
```

### 2. A/B Testing

Compare cache configurations:

```python
# Test similarity threshold impact
cache_a = ResponseCache(ttl_seconds=60, similarity_threshold=0.5)
cache_b = ResponseCache(ttl_seconds=60, similarity_threshold=0.7)

# Run workload...

stats_a = cache_a.get_timing_stats()
stats_b = cache_b.get_timing_stats()

print(f"Config A - Hit rate: {stats_a['cache_hits'] / stats_a['total_get_ops']}")
print(f"Config B - Hit rate: {stats_b['cache_hits'] / stats_b['total_get_ops']}")
```

### 3. Cost Analysis

Estimate cache value:

```python
stats = cache.get_timing_stats()

# Calculate time saved by cache
hits = stats['cache_hits']
avg_provider_latency_ms = 300  # Typical LLM latency
avg_cache_latency_ms = stats['avg_hit_latency_ms']

time_saved_ms = hits * (avg_provider_latency_ms - avg_cache_latency_ms)
print(f"Cache saved {time_saved_ms / 1000:.2f} seconds")
```

### 4. Debugging

Identify performance issues:

```python
stats = cache.get_timing_stats()

# Check if hits are actually faster
if stats['avg_hit_latency_ms'] > stats['avg_miss_latency_ms']:
    print("WARNING: Cache hits slower than misses")
    print("Possible cause: Similarity computation overhead")

# Check latency variance
if stats['p95_get_latency_ms'] > stats['avg_get_latency_ms'] * 3:
    print("WARNING: High latency variance detected")
    print("Some queries are much slower than average")
```

## Redis Cache Timing

The same timing metrics are available for `SharedRedisCache`:

```python
from reliability_lab.cache import SharedRedisCache

cache = SharedRedisCache(
    redis_url="redis://localhost:6379",
    ttl_seconds=60,
    similarity_threshold=0.6
)

# Use cache...
cache.set("query", "response")
result, score = cache.get("query")

# Get timing stats
stats = cache.get_timing_stats()
print(f"Redis GET latency: {stats['avg_get_latency_ms']:.3f} ms")
```

### Expected Redis Latency

Typical latency ranges:

- **Exact match (HGET)**: 1-5 ms
- **Similarity scan (SCAN + HGET)**: 10-100 ms (depends on cache size)
- **SET operations (HSET + EXPIRE)**: 1-5 ms

## Demo

Run the demo script to see timing metrics in action:

```bash
python examples/cache_timing_demo.py
```

This will:
1. Populate cache with sample queries
2. Perform various lookups (hits and misses)
3. Display comprehensive timing statistics
4. Export metrics to JSON

## Testing

Cache timing is tested in `tests/test_cache_timing.py`:

```bash
pytest tests/test_cache_timing.py -v
```

Tests cover:
- GET/SET timing tracking
- Hit/Miss separation
- Privacy query handling
- Empty cache edge cases
- P95 calculation
- False hit classification

## Integration with Metrics System

Cache timing can be integrated into the existing metrics framework:

```python
from reliability_lab.metrics import RunMetrics
from reliability_lab.cache import ResponseCache

cache = ResponseCache(60, 0.6)

# Use cache during load test...

# Export cache metrics
stats = cache.get_timing_stats()
metrics = RunMetrics(
    cache_hits=stats['cache_hits'],
    total_requests=stats['total_get_ops'],
    # ... other metrics
)
```

## Benefits

1. **Visibility**: See actual cache performance in production
2. **Optimization**: Identify slow operations and bottlenecks
3. **Validation**: Verify cache is actually improving performance
4. **Debugging**: Diagnose unexpected behavior
5. **Cost Justification**: Quantify cache value

## Future Enhancements

Potential improvements:

- [ ] Histogram of latency distribution
- [ ] Per-query latency tracking
- [ ] Automatic alerting on threshold violations
- [ ] Integration with metrics dashboards (Prometheus, Grafana)
- [ ] Cache warming strategies based on timing data
- [ ] Adaptive similarity threshold based on latency
