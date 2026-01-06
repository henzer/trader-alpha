FROM python:3.11-slim

WORKDIR /app

COPY api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY data-provider/src /app/src
COPY score-engine/src /app/src_score
COPY graph/src /app/src_graph
COPY api/main.py /app/main.py

RUN cp -r /app/src_score/* /app/src/ && \
    cp -r /app/src_graph/* /app/src/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]