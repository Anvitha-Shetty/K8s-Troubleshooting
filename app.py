import os
from typing import Iterable
import logging
import bson
from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo
from pymongo.errors import PyMongoError
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
from bson import ObjectId

#Creating a new directory
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

 # This handler will write logs to 'app.log' file
file_handler = logging.FileHandler(os.path.join(log_directory, 'app.log')) 
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - studentapp - %(levelname)s - %(message)s')  
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

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

meter = metrics.get_meter(__name__)
counter = meter.create_counter("counter")
counter.add(1)
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

update_success_counter = meter.create_counter(
    "student_updates_total",  
    description="Number of successful student detail updates",
    unit="1",
)

delete_success_counter = meter.create_counter(
    "student_deletions_total",  
    description="Number of successful student deletions",
    unit="1",
)

find_success_counter = meter.create_counter(
    "student_searches_successful",  
    description="Number of successful student searches",
    unit="1",
)

# Error Counters
submit_error_counter = meter.create_counter(
    "submit_error_counter",
    description="Number of errors encountered during student detail submission",
    unit="1",
)

show_error_counter = meter.create_counter(
    "show_error_counter",
    description="Number of errors encountered while retrieving student details",
    unit="1",
)

update_error_counter = meter.create_counter(
    "update_error_counter",
    description="Number of errors encountered while updating student details",
    unit="1",
)

delete_error_counter = meter.create_counter(
    "delete_error_counter",
    description="Number of errors encountered while deleting student",
    unit="1",
)

find_error_counter = meter.create_counter(
    "find_error_counter",
    description="Number of errors encountered while searching students",
    unit="1",
)

# Configure OpenTelemetry logs
logger_provider = LoggerProvider(resource=Resource.create({"service.name": "studentapp"}))
set_logger_provider(logger_provider)
exporter = OTLPLogExporter(insecure=True)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
logging.getLogger().addHandler(handler)

# Initialize Flask application
app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/mydatabase'  # MongoDB connection URI
mongo = PyMongo(app)

mongo.db.students.create_index([('name', 'text'), ('usn', 'text'), ('sem', 'text'), ('section', 'text')])

# Configure PyMongo instrumentation
PymongoInstrumentor().instrument()

# Configure Flask instrumentation
FlaskInstrumentor().instrument_app(app)

# Define routes

# Route for the home page
@app.route('/')
def index():
    return render_template('index.html')

# Route for submitting student details
@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    usn = request.form['usn']
    sem = request.form['sem']
    section = request.form['section']

    existing_student = mongo.db.students.find_one({'usn': usn})
    
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("submit"):
        if existing_student:
            return "Error: USN already exists. Please choose a different USN.", 409  # Conflict status code
    
        try:
            mongo.db.students.insert_one({'_id': usn, 'name': name, 'usn': usn, 'sem': sem, 'section': section})
            forms_submitted_counter.add(1)
            logger.info("New student details submitted: Name=%s, USN=%s, Semester=%s, Section=%s", name, usn, sem, section)
        except PyMongoError as e:
            submit_error_counter.add(1)
            logger.error("Error submitting student details: %s", e)
            #logger.warning("Warning: Failed to submit student details")
            return redirect(url_for('index')), 500

    return redirect(url_for('index'))

@app.route('/show')
def show():
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("show"):
        try:
            students = mongo.db.students.find()
            database_viewers_counter.add(1)
        except Exception as e:
            show_error_counter.add(1)
            logger.error("Error retrieving student details: %s", e)
            return "Error retrieving student details", 500
    return render_template('show.html', students=students)

# Route for editing a student's details
#To fill the form with existing details
@app.route('/edit/<usn>', methods=['GET'])
def edit_student(usn):
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("edit_student"):
        student = mongo.db.students.find_one({'usn': usn})
        if student:
            return render_template('edit.html', student=student)
        else:
            return "Student not found", 404

#To make changes after submission
@app.route('/update/<usn>', methods=['POST'])
def update(usn):
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("update_student"):
        try:
            name = request.form['name']
            new_usn = request.form['usn'] 
            sem = request.form['sem']
            section = request.form['section']

            if new_usn != usn:
                existing_student = mongo.db.students.find_one({'usn': new_usn})
                if existing_student:
                    return "USN already exists", 409 

            mongo.db.students.update_one({'usn': usn}, {'$set': {'name': name, 'usn': new_usn, 'sem': sem, 'section': section}})

            update_success_counter.add(1)
            
            logger.info("Student details updated: Name=%s, USN=%s, Semester=%s, Section=%s", name, new_usn, sem, section)
            
        except PyMongoError as e:
            update_error_counter.add(1)
            logger.error("Error updating student details: %s", e)
            #logger.warning("Warning: Failed to update student details")
            return redirect(url_for('show')), 500
        
    return redirect(url_for('show'))

# Route for deleting a student
@app.route('/delete/<usn>', methods=['GET'])
def delete(usn):
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("delete_student"):
        try:
            mongo.db.students.delete_one({'usn': usn})
            logger.info("Student deleted: USN=%s", usn)
            delete_success_counter.add(1)

        except PyMongoError as e:
            delete_error_counter.add(1)
            logger.error("Error deleting student: %s", e)
            #logger.warning("Warning: Failed to delete student")
            return redirect(url_for('show')), 500

    return redirect(url_for('show'))

@app.route('/find', methods=['POST'])
def find():
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("find"):
        query = request.form['query']
        try:
            students = mongo.db.students.find({'$text': {'$search': query}})
            find_success_counter.add(1)
            logger.info("Search query executed: %s", query)
        except PyMongoError as e:
            find_error_counter.add(1)
            logger.error("Error executing search query: %s", e)
            #logger.warning("Warning: Failed to execute search query")
            return redirect(url_for('show')), 500
    
    return render_template('show.html', students=students)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
