FROM python:3.12-slim

RUN pip install --upgrade pip \
    && pip install pipenv 

WORKDIR /app

COPY Pipfile Pipfile.lock /app/

RUN pipenv install --system --deploy --ignore-pipfile

COPY /app /app

EXPOSE 50051

CMD ["python", "main.py"]
