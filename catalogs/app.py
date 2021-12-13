import os
from flask import Flask
from flask_redis import FlaskRedis

from waitress import serve

FLASK_SERVICE_NAME = os.getenv('FLASK_SERVICE_NAME', 'NO_SERVICE')
POD_NAME = os.getenv('HOSTNAME', 'NO_NAME')

app = Flask(__name__)

app.config['REDIS_URL'] = os.getenv('REDIS_URL', 'redis://redis:6379')

KEY_REQ_POD = 'flask:catalogs:pod:' + POD_NAME
KEY_PER_MICROSERVICE = 'flask:catalogs'
KEY_TOTAL_COUNT = 'flask:total'

redis_client = FlaskRedis(app)

def get_requests_count():
    pod_count = 0
    request_count = 0
    microservice_count = 0

    if redis_client.get(KEY_REQ_POD) is not None:
        pod_count = int(redis_client.get(KEY_REQ_POD))
        pod_count += 1

    if redis_client.get(KEY_PER_MICROSERVICE) is not None:
        request_count = int(redis_client.get(KEY_PER_MICROSERVICE))
        microservice_count += 1

    if redis_client.get(KEY_TOTAL_COUNT) is not None:
        request_count = int(redis_client.get(KEY_TOTAL_COUNT))
        request_count += 1
    
    redis_client.set(KEY_TOTAL_COUNT, request_count)
    redis_client.set(KEY_PER_MICROSERVICE, microservice_count)
    redis_client.set(KEY_REQ_POD, pod_count)

    return request_count, microservice_count, pod_count


@app.route('/')
def hello():    
    request_count, microservice_count, pod_count = get_requests_count()
    return f"Service: {FLASK_SERVICE_NAME} from {POD_NAME}. Pod: {microservice_count}, service: {request_count}, total: {pod_count}."

if __name__ == '__main__':
    serve(app, host="0.0.0.0", port=8081)
