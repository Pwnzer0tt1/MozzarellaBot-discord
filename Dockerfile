FROM python:3.11-slim

RUN mkdir -p /execute/modules
WORKDIR /execute
RUN apt-get update && apt-get install -y build-essential
ADD ./requirements.txt /execute/requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r /execute/requirements.txt --no-warn-script-location
COPY . /execute/

CMD ["python", "-u", "/execute/bot.py"]
