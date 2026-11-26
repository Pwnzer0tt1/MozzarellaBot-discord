FROM python:3.15-slim

WORKDIR /execute
# build-essential is kept for dependencies without prebuilt wheels for the current Python (e.g. frozenlist)
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /execute/requirements.txt
RUN pip3 install --no-cache-dir --upgrade pip \
    && pip3 install --no-cache-dir -r /execute/requirements.txt --no-warn-script-location
COPY . /execute/

CMD ["python", "-u", "/execute/bot.py"]
