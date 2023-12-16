FROM ubuntu

RUN apt-get update
RUN apt-get install -y curl



WORKDIR /app

COPY requirement.txt .

RUN pip install -r requirement.txt

COPY . .

EXPOSE 8008