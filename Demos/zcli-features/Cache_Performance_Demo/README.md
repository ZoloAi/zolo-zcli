# 📦 Cache Performance Demo

Demonstrates zCLI's dual-layer caching system with real-time performance metrics.

## Features

- **Schema Caching**: Parse zSchema files once, cache indefinitely
- **Query Result Caching**: Cache database query results with configurable TTL
- **Real-time Stats**: See cache hits, misses, and performance improvements
- **Interactive Testing**: Test different cache scenarios with live metrics

## Quick Start

1. **Start the backend:**
   ```bash
   cd Demos/zcli-features/Cache_Performance_Demo
   python3 run_cache_demo.py
   ```

2. **Open the demo:**
   - Navigate to: `http://127.0.0.1:5500/Demos/zcli-features/Cache_Performance_Demo/Cache_Performance_Demo.html`
   - Or open `Cache_Performance_Demo.html` in your browser with Live Server

3. **Run tests:**
   - **Schema Cache Test**: Shows 10-100x speedup on cached schema requests
   - **Query Cache Test**: Shows 5-50x speedup on cached query results
   - **Set TTL**: Configure cache expiration time
   - **Clear Cache**: Reset all caches and stats

## Architecture

```
Cache_Performance_Demo/
├── Cache_Performance_Demo.html    # Frontend demo
├── run_cache_demo.py              # Backend server
├── zSchema.cache_demo.yaml        # Database schema with sample data
├── zUI.cache_demo.yaml            # UI commands
└── README.md                      # This file
```

## How It Works

### Schema Caching
- First request: Parse YAML file (~50-200ms)
- Subsequent requests: Return cached schema (~0.5-2ms)
- **Result**: 10-100x faster

### Query Result Caching
- First query: Execute SQL and fetch results (~10-100ms)
- Cached queries: Return stored results (~1-5ms)
- TTL-based expiration (default: 60 seconds)
- **Result**: 5-50x faster

## Sample Data

The demo includes 8 sample products across 3 categories:
- Electronics (5 items)
- Furniture (2 items)
- Stationery (1 item)

Perfect for testing query caching with realistic data!

