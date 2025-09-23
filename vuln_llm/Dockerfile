FROM python:3.11-slim
WORKDIR /app
COPY mock_llm.py /app/
RUN pip install fastapi uvicorn
EXPOSE 8080
CMD ["uvicorn","mock_llm:app","--host","0.0.0.0","--port","8080"]
