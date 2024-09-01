from fastapi import FastAPI

app = FastAPI()


@app.get('/', description='Root endpoint')
def root():
    return {'message': 'Hello World'}
