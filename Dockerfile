FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /map-backend
WORKDIR /map-backend
COPY requirements.txt /map-backend/requirements.txt
RUN pip install -r requirements.txt
COPY . /map-backend/
#CMD [ "python3", "manage.py", "runserver" ]
