# Kibana Dashboards for RAG Comparison Analytics

This directory contains Kibana dashboard configurations for visualizing RAG (Retrieval-Augmented Generation) comparison metrics between pgvector and Elasticsearch.

## Overview

The dashboards visualize data from the `cv_rag_logs` Elasticsearch index, which logs every comparison query including:
- Query text
- Scores for both systems
- Retrieval latency
- Retrieved chunk details
- LLM evaluation results

## Setup Instructions

### 1. Access Kibana

If you're running Elasticsearch locally or via Railway, access Kibana at:
- Local: `http://localhost:5601`
- Railway: Check your Railway environment variables for `KIBANA_URL`

### 2. Create Index Pattern

1. Navigate to **Stack Management** → **Index Patterns**
2. Click **Create index pattern**
3. Enter index pattern: `cv_rag_logs`
4. Select time field: `timestamp`
5. Click **Create index pattern**

### 3. Import Dashboards

#### Option 1: Manual Import (Recommended)

1. Navigate to **Stack Management** → **Saved Objects**
2. Click **Import**
3. Select the JSON file: `rag_comparison_dashboard.ndjson`
4. Click **Import**

#### Option 2: Manual Creation

Follow the visualization guide in `visualization_guide.md` to create each visualization manually.

## Available Dashboards

### 1. RAG Comparison Overview Dashboard

**File**: `rag_comparison_dashboard.ndjson`

**Visualizations**:
- **Average Scores Bar Chart**: Horizontal bars showing average scores for pgvector vs Elasticsearch
- **Score Distribution Histogram**: Distribution of scores (0-100) for both systems
- **Win Rate Pie Chart**: Percentage of wins for pgvector, Elasticsearch, and ties
- **Score Trends Line Chart**: Time-series visualization of score evolution
- **Latency Comparison Bar Chart**: Average retrieval time comparison
- **Detailed Query Table**: Searchable table with all query details

**Use Cases**:
- Quick performance comparison at a glance
- Identify which system performs better on average
- Spot trends over time
- Deep-dive into specific queries

### 2. Performance Metrics Dashboard

**File**: `performance_metrics_dashboard.ndjson`

**Visualizations**:
- **Latency Heatmap**: Time-based latency patterns
- **Score Scatter Plot**: pgvector score vs Elasticsearch score
- **Chunk Retrieval Stats**: Average number of chunks retrieved
- **Query Volume Timeline**: Number of queries over time

**Use Cases**:
- Performance optimization
- Latency analysis
- Capacity planning
- Quality assurance

## Data Schema

### Index: `cv_rag_logs`

```json
{
  "timestamp": "2026-01-02T12:34:56.789Z",
  "query_text": "What experience does Michael have with databases?",

  "pgvector": {
    "score": 95.0,
    "retrieval_time_ms": 45.3,
    "top_scores": [0.92, 0.87, 0.82],
    "chunk_count": 3,
    "chunk_ids": ["pgv_0", "pgv_1", "pgv_2"],
    "answer_length": 145
  },

  "elasticsearch": {
    "score": 88.0,
    "retrieval_time_ms": 32.1,
    "top_scores": [0.89, 0.85, 0.79],
    "chunk_count": 3,
    "chunk_ids": ["es_0", "es_1", "es_2"],
    "answer_length": 152
  },

  "evaluation": {
    "winner": "pgvector",
    "reasoning": "More accurate and concise answer",
    "pgvector_score": 95.0,
    "elasticsearch_score": 88.0,
    "score_difference": 7.0
  },

  "llm_provider": "grok",
  "user_id": "7ba82628-49d0-4a06-a724-11790fa3fc91"
}
```

## Key Metrics (KPIs)

1. **Average Score**
   - Field: `evaluation.pgvector_score` and `evaluation.elasticsearch_score`
   - Type: Metric (Average)
   - Goal: Higher is better (0-100 scale)

2. **Win Rate**
   - Field: `evaluation.winner`
   - Type: Terms aggregation
   - Goal: Track which system wins more often

3. **Average Latency**
   - Field: `pgvector.retrieval_time_ms` and `elasticsearch.retrieval_time_ms`
   - Type: Metric (Average)
   - Goal: Lower is better

4. **Score Difference**
   - Field: `evaluation.score_difference`
   - Type: Metric (Average)
   - Goal: Shows how close the systems perform

## Refresh and Updates

- Data is logged in real-time as users perform comparisons
- Dashboards auto-refresh every 30 seconds (configurable)
- Index is refreshed automatically by Elasticsearch

## Troubleshooting

### Dashboard shows "No results found"

1. Check if index exists: `GET cv_rag_logs/_count`
2. Run some test queries through the comparison endpoint
3. Refresh the index pattern in Kibana
4. Verify time range includes recent data

### Visualizations not updating

1. Click the refresh button (🔄) in Kibana
2. Adjust the time picker to include recent data
3. Force index refresh: `POST cv_rag_logs/_refresh`

### Import fails

1. Ensure Kibana version compatibility (tested on 8.x)
2. Create index pattern manually first
3. Check Kibana logs for detailed errors

## Example Queries

### Get total query count
```
GET cv_rag_logs/_count
```

### Get recent queries
```
GET cv_rag_logs/_search
{
  "size": 10,
  "sort": [{"timestamp": "desc"}]
}
```

### Get average scores
```
GET cv_rag_logs/_search
{
  "size": 0,
  "aggs": {
    "avg_pgvector": {"avg": {"field": "evaluation.pgvector_score"}},
    "avg_elasticsearch": {"avg": {"field": "evaluation.elasticsearch_score"}}
  }
}
```

## Next Steps

1. **Customize dashboards** - Add your own visualizations
2. **Set up alerts** - Get notified when performance drops
3. **Export reports** - Generate PDF/PNG reports for stakeholders
4. **Create filters** - Filter by LLM provider, user, time range

## Support

For issues or questions:
- Check Elasticsearch logs: `railway logs elasticsearch`
- Check backend logs: `railway logs backend`
- Review Kibana documentation: https://www.elastic.co/guide/en/kibana/current/index.html
