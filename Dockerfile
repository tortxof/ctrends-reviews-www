FROM ubuntu:trusty
MAINTAINER Daniel Jones <tortxof@gmail.com>

RUN apt-get install -y python3-setuptools
RUN easy_install3 pip
COPY requirements.txt /app/
RUN pip3 install -r /app/requirements.txt

WORKDIR /app

EXPOSE 5000

CMD ["python3", "app.py"]
