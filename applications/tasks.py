from cms.celery import app

@app.task
def hello_world():
    print("hello world")
