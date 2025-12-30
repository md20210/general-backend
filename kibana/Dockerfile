# Kibana Dockerfile for Railway
FROM docker.elastic.co/kibana/kibana:8.11.3

# Copy custom configuration
COPY kibana.yml /usr/share/kibana/config/kibana.yml

# Expose Kibana port
EXPOSE 5601

# Run Kibana
CMD ["kibana"]
