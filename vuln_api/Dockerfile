FROM python:3.11-slim
WORKDIR /app
COPY api.py /app/
RUN pip install flask
EXPOSE 5000
CMD ["python","api.py"]
