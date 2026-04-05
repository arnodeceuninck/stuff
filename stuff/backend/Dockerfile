FROM arnodece/framework-backend-base:0.0.1

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY src/ ./src/

CMD ["src.main:app", "--host", "0.0.0.0", "--port", "8000"]