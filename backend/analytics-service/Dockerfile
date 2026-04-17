FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir --upgrade pip \
	&& pip install --no-cache-dir -r requirements.txt

COPY app ./app

RUN addgroup --system appgroup \
	&& adduser --system --ingroup appgroup appuser \
	&& chown -R appuser:appgroup /app

USER appuser

EXPOSE 8003

CMD ["python", "-m", "app.main"]
