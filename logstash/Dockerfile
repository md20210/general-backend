# Logstash Dockerfile for Railway
FROM docker.elastic.co/logstash/logstash:8.11.3

# Copy pipeline configurations
COPY pipelines.yml /usr/share/logstash/config/pipelines.yml
COPY *.conf /usr/share/logstash/pipeline/

# Expose HTTP input ports for each pipeline
EXPOSE 8080 8081 8082

# Run Logstash
CMD ["logstash"]
