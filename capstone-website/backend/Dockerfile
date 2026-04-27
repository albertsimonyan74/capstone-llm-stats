FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py user_study.py ./
COPY static_data/ ./static_data/
RUN mkdir -p data && echo "[]" > data/user_study_results.json
ENV DATA_ROOT=/app/static_data
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
