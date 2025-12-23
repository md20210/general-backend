# Ollama Service for Railway (CPU-optimized)
FROM ollama/ollama:latest

# Environment variables
ENV OLLAMA_HOST=0.0.0.0:11434
ENV OLLAMA_ORIGINS=*

# Expose Ollama port
EXPOSE 11434

# Create startup script that pulls model and starts server
RUN echo '#!/bin/bash\n\
set -e\n\
echo "Starting Ollama server in background..."\n\
ollama serve &\n\
OLLAMA_PID=$!\n\
echo "Waiting for Ollama to be ready..."\n\
sleep 10\n\
echo "Pulling llama3.2:3b model..."\n\
ollama pull llama3.2:3b && echo "Model pulled successfully!" || echo "Model pull failed"\n\
echo "Ollama is ready!"\n\
wait $OLLAMA_PID\n\
' > /start.sh && chmod +x /start.sh

# Start Ollama with model pre-loading
CMD ["/start.sh"]
