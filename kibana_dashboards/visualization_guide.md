# Kibana Visualization Guide - Manual Creation

This guide walks you through creating each visualization manually in Kibana.

## Prerequisites

1. Kibana is accessible and running
2. Index pattern `cv_rag_logs` is created with `timestamp` as the time field
3. You have run at least a few test queries to populate data

---

## Visualization 1: Average Scores Bar Chart

**Purpose**: Compare average scores between pgvector and Elasticsearch

**Steps**:
1. Navigate to **Visualize** → **Create visualization**
2. Select **Horizontal Bar** chart type
3. Choose index pattern: `cv_rag_logs`

**Configuration**:
- **Metrics**:
  - Y-axis 1: `Aggregation: Average`, `Field: evaluation.pgvector_score`
  - Y-axis 2: `Aggregation: Average`, `Field: evaluation.elasticsearch_score`
- **Buckets**:
  - X-axis: `Aggregation: Terms`, `Field: evaluation.winner`, `Order: Descending`, `Size: 10`

**Chart Options**:
- Chart type: Horizontal Bar
- Legend position: Right
- Show values on bars: Yes

**Save**: Name it "Average Scores - pgvector vs Elasticsearch"

---

## Visualization 2: Score Distribution Histogram

**Purpose**: Show distribution of scores (0-100) for both systems

**Steps**:
1. **Visualize** → **Create visualization** → **Histogram**
2. Index pattern: `cv_rag_logs`

**Configuration**:
- **Metrics**:
  - Y-axis: `Aggregation: Count`
- **Buckets**:
  - X-axis: `Aggregation: Histogram`, `Field: evaluation.pgvector_score`, `Interval: 10`
  - Split series: `Aggregation: Histogram`, `Field: evaluation.elasticsearch_score`, `Interval: 10`

**Chart Options**:
- X-axis label: "Score Range"
- Y-axis label: "Number of Queries"
- Legend: Right

**Save**: "Score Distribution Histogram"

---

## Visualization 3: Win Rate Pie Chart

**Purpose**: Show percentage of wins for pgvector, Elasticsearch, and ties

**Steps**:
1. **Visualize** → **Create visualization** → **Pie**
2. Index pattern: `cv_rag_logs`

**Configuration**:
- **Metrics**:
  - Slice size: `Aggregation: Count`
- **Buckets**:
  - Split slices: `Aggregation: Terms`, `Field: evaluation.winner`, `Order: Descending`, `Size: 5`

**Chart Options**:
- Donut: No (use full pie)
- Show labels: Yes
- Show values: Yes
- Legend position: Right

**Colors** (optional customization):
- pgvector: Blue (#3399FF)
- elasticsearch: Orange (#FF9933)
- tie: Gray (#999999)

**Save**: "Win Rate Pie Chart"

---

## Visualization 4: Score Trends Line Chart

**Purpose**: Visualize how scores change over time

**Steps**:
1. **Visualize** → **Create visualization** → **Line**
2. Index pattern: `cv_rag_logs`

**Configuration**:
- **Metrics**:
  - Y-axis 1: `Aggregation: Average`, `Field: evaluation.pgvector_score`
  - Y-axis 2: `Aggregation: Average`, `Field: evaluation.elasticsearch_score`
- **Buckets**:
  - X-axis: `Aggregation: Date Histogram`, `Field: timestamp`, `Interval: Hourly`

**Chart Options**:
- Line interpolation: Linear
- Show dots: Yes
- X-axis label: "Time"
- Y-axis label: "Average Score"
- Legend: Right

**Save**: "Score Trends Over Time"

---

## Visualization 5: Latency Comparison Bar Chart

**Purpose**: Compare average retrieval time between systems

**Steps**:
1. **Visualize** → **Create visualization** → **Horizontal Bar**
2. Index pattern: `cv_rag_logs`

**Configuration**:
- **Metrics**:
  - Y-axis 1: `Aggregation: Average`, `Field: pgvector.retrieval_time_ms`, `Custom Label: pgvector Latency`
  - Y-axis 2: `Aggregation: Average`, `Field: elasticsearch.retrieval_time_ms`, `Custom Label: Elasticsearch Latency`

**Chart Options**:
- Mode: Normal (not stacked)
- X-axis label: "Latency (ms)"
- Legend: Right
- Threshold line (optional): 100ms (yellow), 200ms (red)

**Save**: "Latency Comparison"

---

## Visualization 6: Detailed Query Analysis Table

**Purpose**: Searchable table with all query details

**Steps**:
1. **Visualize** → **Create visualization** → **Data Table**
2. Index pattern: `cv_rag_logs`

**Configuration**:
- **Metrics**:
  - Metric 1: `Aggregation: Count`, `Custom Label: Queries`
  - Metric 2: `Aggregation: Average`, `Field: evaluation.pgvector_score`, `Custom Label: Avg pgvector Score`
  - Metric 3: `Aggregation: Average`, `Field: evaluation.elasticsearch_score`, `Custom Label: Avg ES Score`
  - Metric 4: `Aggregation: Average`, `Field: pgvector.retrieval_time_ms`, `Custom Label: pgvector Latency`
  - Metric 5: `Aggregation: Average`, `Field: elasticsearch.retrieval_time_ms`, `Custom Label: ES Latency`

- **Buckets**:
  - Split rows 1: `Aggregation: Terms`, `Field: query_text.keyword`, `Order: Descending`, `Size: 20`
  - Split rows 2: `Aggregation: Terms`, `Field: evaluation.winner`, `Order: Descending`, `Size: 5`

**Table Options**:
- Per page: 10
- Show total: Yes
- Percentage column: Off

**Save**: "Detailed Query Analysis Table"

---

## Dashboard Creation

**Steps**:
1. Navigate to **Dashboard** → **Create dashboard**
2. Click **Add from library**
3. Add all 6 visualizations created above

**Layout Suggestion**:

```
+------------------------+------------------------+
| Average Scores Bar     | Score Distribution     |
| (24 cols x 15 rows)    | Histogram              |
|                        | (24 cols x 15 rows)    |
+------------------------+------------------------+
| Win Rate Pie    | Score Trends | Latency       |
| (16 cols x 15)  | Line Chart   | Comparison    |
|                 | (16 cols x15)| (16 cols x15) |
+-----------------+--------------+---------------+
| Detailed Query Analysis Table                  |
| (48 cols x 20 rows)                            |
+------------------------------------------------+
```

**Dashboard Settings**:
- **Time range**: Last 24 hours (adjustable)
- **Auto-refresh**: 30 seconds
- **Title**: "RAG Comparison Dashboard - pgvector vs Elasticsearch"
- **Description**: "Real-time analytics for RAG system comparison"

**Save**: "RAG Comparison Dashboard - pgvector vs Elasticsearch"

---

## KPI Metrics (Bonus Visualizations)

### Total Queries Metric
1. **Visualize** → **Metric**
2. Metric: `Aggregation: Count`
3. Custom label: "Total Queries"
4. Font size: Large

### Average Score Difference Metric
1. **Visualize** → **Metric**
2. Metric: `Aggregation: Average`, `Field: evaluation.score_difference`
3. Custom label: "Avg Score Difference"
4. Format: Decimal (2 places)

### Win Percentage for Elasticsearch
1. **Visualize** → **Metric**
2. Metric: `Aggregation: Count`
3. Bucket filter: `evaluation.winner: "elasticsearch"`
4. Calculate percentage with scripted metric

---

## Advanced: Scripted Fields

### Create "Performance Gap" Field

1. Navigate to **Stack Management** → **Index Patterns** → `cv_rag_logs`
2. Click **Scripted fields** → **Add scripted field**

**Configuration**:
- Name: `performance_gap`
- Language: `painless`
- Type: `number`
- Format: `Number (2 decimals)`
- Script:
```painless
doc['evaluation.elasticsearch_score'].value - doc['evaluation.pgvector_score'].value
```

This creates a calculated field showing the performance gap (positive = ES wins, negative = pgvector wins)

### Create "Is Fast Query" Boolean Field

**Configuration**:
- Name: `is_fast_query`
- Language: `painless`
- Type: `boolean`
- Script:
```painless
(doc['pgvector.retrieval_time_ms'].value < 50) && (doc['elasticsearch.retrieval_time_ms'].value < 50)
```

Use this to filter and analyze only fast queries.

---

## Filters and Queries

### Useful Kibana Query Language (KQL) Filters

**Show only pgvector wins**:
```
evaluation.winner: "pgvector"
```

**Show close competitions (score difference < 10)**:
```
evaluation.score_difference < 10
```

**Show slow queries (either system > 100ms)**:
```
pgvector.retrieval_time_ms > 100 OR elasticsearch.retrieval_time_ms > 100
```

**Show queries using Grok LLM**:
```
llm_provider: "grok"
```

**Filter by specific user**:
```
user_id: "7ba82628-49d0-4a06-a724-11790fa3fc91"
```

---

## Tips for Best Results

1. **Color coding**: Use consistent colors (pgvector = blue, Elasticsearch = orange)
2. **Time range**: Default to "Last 24 hours" but make it adjustable
3. **Auto-refresh**: Set to 30 seconds for live monitoring
4. **Threshold lines**: Add threshold lines at 80% score (good) and 90% (excellent)
5. **Export**: Save dashboard for backup via **Share** → **Download as JSON**
6. **Clone**: Duplicate dashboard to experiment with variations

---

## Troubleshooting

**"No results found"**:
- Check time range includes when you ran queries
- Verify index has data: `GET cv_rag_logs/_count`
- Refresh index pattern: Stack Management → Index Patterns → Refresh

**Aggregation errors**:
- Ensure field types are correct (scores = float, timestamp = date)
- Check field names match exactly (case-sensitive)

**Slow dashboards**:
- Reduce time range
- Limit table rows (e.g., top 10 instead of 100)
- Use smaller aggregation intervals

---

## Next Steps

1. **Alerts**: Set up Kibana alerts for performance drops
2. **Reports**: Schedule PDF reports for stakeholders
3. **Canvas**: Create executive summary workpad
4. **ML Jobs**: Use Kibana ML to detect anomalies in scores
