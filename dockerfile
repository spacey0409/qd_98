FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

ENV TZ=Asia/Shanghai

# Install python application dependencies
COPY . /app
WORKDIR /app

RUN echo "${TZ}" > /etc/timezone \
&& ln -sf /usr/share/zoneinfo/${TZ} /etc/localtime \
&& apt update \
&& apt install -y tzdata

RUN pip install -r requirements.txt
RUN playwright install
#RUN pip install pytest-playwright
#RUN playwright install --with-deps chromium

