from python:3.11

WORKDIR /code
COPY ./ .

RUN apt-get update -y
RUN apt-get -y install wkhtmltopdf



RUN pip install --upgrade pip
RUN pip install -e .
RUN pip install -r requirements.txt



EXPOSE 8000
CMD ["uvicorn", "sym.main:app", "--port", "8000", "--host", "0.0.0.0"]