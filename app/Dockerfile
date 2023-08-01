FROM python:3.9

ENV PYTHONUNBUFFERED 1
ENV OTEL_PYTHON_LOG_CORRELATION true

COPY . /code/
WORKDIR /code/

RUN pip install --upgrade pip
RUN pip install opentelemetry-distro
RUN pip install opentelemetry-exporter-otlp-proto-grpc
RUN pip install Click
RUN pip install Flask
RUN pip install itsdangerous
RUN pip install Jinja2
RUN pip install MarkupSafe
RUN pip install Werkzeug
RUN pip install speedtest-cli
RUN pip install schedule
RUN pip install redis

RUN opentelemetry-bootstrap -a install

ENTRYPOINT ["opentelemetry-instrument"]
CMD [ "flask", "run", "--port=5000", "--host=0.0.0.0" ]

