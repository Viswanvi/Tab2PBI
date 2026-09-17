FROM python:3.11-slim AS build
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python scripts/vendor_engine.py

FROM python:3.11-slim
WORKDIR /app
COPY --from=build /usr/local /usr/local
COPY --from=build /app /app
ENV TAB2PBI_WORKSPACE=/data/workspace
EXPOSE 8000
CMD ["uvicorn","tab2pbi.main:app","--host","0.0.0.0","--port","8000"]
