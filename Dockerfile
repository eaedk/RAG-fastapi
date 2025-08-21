FROM python:3.13.5-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
COPY . ./

RUN pip3 install -r requirements.txt

EXPOSE 7860

# HEALTHCHECK CMD curl --fail http://localhost:8000/_stcore/health

ENTRYPOINT ["uvicorn", "_app:app", "", "--host=0.0.0.0 ", " --port=7860", "--reload"]