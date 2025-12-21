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
echo "Starting Ollama server..."\n\
ollama serve &\n\
OLLAMA_PID=$!\n\
echo "Waiting for Ollama to be ready..."\n\
sleep 5\n\
echo "Pulling llama3.2:3b model (CPU-optimized, small, fast)..."\n\
ollama pull llama3.2:3b || echo "Model pull failed, will retry on next request"\n\
echo "Ollama ready with llama3.2:3b!"\n\
wait $OLLAMA_PID\n\
' > /start.sh && chmod +x /start.sh

# Start Ollama with model pre-loading
CMD ["/start.sh"]
