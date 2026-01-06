FROM python:3.11-slim

WORKDIR /app

COPY data-provider/ /app/data-provider/
COPY score-engine/ /app/score-engine/
COPY graph/ /app/graph/
COPY api/ /app/api/

RUN pip install --no-cache-dir -e /app/data-provider
RUN pip install --no-cache-dir -e /app/score-engine
RUN pip install --no-cache-dir -e /app/graph

WORKDIR /app/api

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]