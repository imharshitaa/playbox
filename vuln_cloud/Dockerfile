FROM python:3.11-slim
WORKDIR /app
COPY app.py /app/
RUN pip install flask requests
EXPOSE 9100
CMD ["python","app.py"]
