FROM python:3.12

WORKDIR /code

COPY ./app/requirements.txt /code/app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/app/requirements.txt

COPY . .

EXPOSE 7860

WORKDIR /code/app

CMD ["shiny", "run", "app.py", "--host", "0.0.0.0", "--port", "7860"]
