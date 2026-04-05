FROM arnodece/framework-backend-base:0.0.1

COPY pyproject.toml .
RUN pip install .  # installs only app-specific deps
COPY src/ ./src/

CMD ["src.main:app", "--host", "0.0.0.0", "--port", "8000"]