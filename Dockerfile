FROM python:slim-bullseye

RUN mkdir -p /execute/modules
WORKDIR /execute

ADD ./requirements.txt /execute/requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r /execute/requirements.txt --no-warn-script-location
COPY . /execute/

CMD ["python", "-u", "/execute/bot.py"]
