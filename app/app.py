from flask import Flask, Response
from opentelemetry import metrics, trace
from opentelemetry.sdk.trace import TracerProvider
import logging, speedtest, threading, redis, time, os

provider = TracerProvider()
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)
app = Flask(__name__)

r = redis.Redis(host='localhost', port=6379, db=0, charset="utf-8", decode_responses=True)

## Logging configuration
FORMAT = ('%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] [trace_id=%(otelTraceID)s span_id=%(otelSpanID)s resource.service.name=%(otelServiceName)s trace_sampled=%(otelTraceSampled)s] - %(message)s')

werkzeug = logging.getLogger('werkzeug')
if len(werkzeug.handlers) == 1:
    formatter = logging.Formatter(FORMAT)
    werkzeug.handlers[0].setFormatter(formatter)


if (os.environ.get('LOG_TO_FILE') == 'true'):
    logging.basicConfig(filename="/code/out.log", 
					format=FORMAT, 
					filemode='w') 
    print('logging to file')
else:
    logging.basicConfig(format=FORMAT)


log = logging.getLogger(__name__)
log.level = logging.INFO


### Metric setup

meter = metrics.get_meter("speedtest")

upload_histogram = meter.create_histogram(
    name="speedtest.upload.histogram",
    description="TODO",
    unit="",
    )

download_histogram = meter.create_histogram(
    name="speedtest.download.histogram",
    description="TODO",
    unit="",
    )
###


def measure_speeds():
    while True:
        with tracer.start_as_current_span("get_speed"):
            span = trace.get_current_span()
            st = speedtest.Speedtest()
            best_serv=st.get_best_server()
            log.info(best_serv)
            download=round((st.download()*0.000001),2)
            upload=round((st.upload()*0.000001),2)
            span.add_event( "log", {
                "speed.upload": upload,
                "speed.download": download,
            })
            r.set('upload', upload)
            r.set('download', download)
            download_histogram.record(download, attributes={"attr1": "value1"})
            upload_histogram.record(upload, attributes={"attr1": "value1"})
        time.sleep(300)

def start_scheduling():
    speedtest_thread = threading.Thread(target=measure_speeds, name="speedtester")
    speedtest_thread.start()

start_scheduling()


###### Endpoints

@app.route("/upload")
def upload():
    upload = str(r.get('upload'))
    log.info('Upload route hit: ' + upload + "MB/s")
    return Response(upload, status=200)

@app.route("/download")
def download():
    download = str(r.get('download'))
    log.info('Download route hit: ' + download + "MB/s") 
    return Response(download, status=200)


@app.route("/best_serv")
def best_serv():
    best_serv = r.get('best_serv')
    log.info('best server details: ' + best_serv)
    return Response(best_serv, status=200)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8888)
