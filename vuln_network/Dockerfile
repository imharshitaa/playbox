FROM python:3.11-slim
WORKDIR /app
COPY tcp_server.py /app/
COPY app.py /app/
RUN pip install flask requests
EXPOSE 9001
EXPOSE 9101
CMD ["python","app.py"]
