FROM python:3.13

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir -r /code/requirements.txt

COPY ./app /code/app
COPY ./main.py /code/main.py

CMD [ "fastapi", "run", "main.py", "--port", "80" ]