# Kibana 8.12.0 - matches Elasticsearch version
FROM docker.elastic.co/kibana/kibana:8.12.0

# Copy custom Kibana configuration
COPY kibana.yml /usr/share/kibana/config/kibana.yml

# Expose Kibana port
EXPOSE 5601

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=5 \
  CMD curl -f http://localhost:5601/api/status || exit 1

# Start Kibana
CMD ["/usr/local/bin/kibana-docker"]
