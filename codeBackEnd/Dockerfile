FROM python:3.11.9-debian

WORKDIR ~/Desktop

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONNUNBUFFERED 1

RUN pip install --upgrade pip
COPY ../start_dev_process.sh ~/Desktop/app/start_dev_process.sh
COPY ./requir.txt ~/Desktop/app/requir.txt
RUN pip install -r ~/Desktop/app/requir.txt

ENTRYPOINT ["~/Desktop/app/start_dev_process.sh"]
