from typing import Iterable
import logging
from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.pymongo import PymongoInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure OpenTelemetry trace
trace.set_tracer_provider(TracerProvider(resource=Resource.create({"service.name": "studentapp"})))

# Create an OTLP span exporter for sending traces to the collector
span_exporter = OTLPSpanExporter(insecure=True)

# Add a span processor to batch and export spans
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(span_exporter)
)

# Configure OpenTelemetry metrics
exporter = OTLPMetricExporter(insecure=True)
reader = PeriodicExportingMetricReader(exporter)
provider = MeterProvider(resource=Resource.create({"service.name": "studentapp"}), metric_readers=[reader])
metrics.set_meter_provider(provider)

def observable_counter_func(options: metrics.CallbackOptions) -> Iterable[metrics.Observation]:
    yield metrics.Observation(1, {})

meter = metrics.get_meter(__name__)

forms_submitted_counter = meter.create_counter(
    name="forms_submitted_counter",
    description="Number of forms submitted",
    unit="1",
)

database_viewers_counter = meter.create_counter(
    name="Database_viewers_counter",
    description="Number of viewers",
    unit="1",
)

observable_counter = meter.create_observable_counter("submit_counter", [observable_counter_func],)

# Configure OpenTelemetry logs
logger_provider = LoggerProvider(resource=Resource.create({"service.name": "studentapp"}))
set_logger_provider(logger_provider)
exporter = OTLPLogExporter(insecure=True)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
logging.getLogger().addHandler(handler)

# Initialize Flask application
app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://mongodb:27017/mydatabase'  # MongoDB connection URI
mongo = PyMongo(app)

# Configure PyMongo instrumentation
PymongoInstrumentor().instrument()

# Configure Flask instrumentation
FlaskInstrumentor().instrument_app(app)

# Define routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    forms_submitted_counter.add(1)
    name = request.form['name']
    usn = request.form['usn']
    sem = request.form['sem']
    section = request.form['section']

    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("submit"):
        mongo.db.students.insert_one({'name': name, 'usn': usn, 'sem': sem, 'section': section})
        
    logger.info("New student details submitted: Name=%s, USN=%s, Semester=%s, Section=%s", name, usn, sem, section)
    return redirect(url_for('index'))

@app.route('/show')
def show():
    database_viewers_counter.add(1)
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("show"):
        students = mongo.db.students.find()
    
    return render_template('show.html', students=students)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
