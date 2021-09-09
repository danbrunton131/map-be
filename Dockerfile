FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /map-backend
WORKDIR /map-backend
   
# install dependencies
RUN pip install --upgrade pip
COPY requirements.txt /map-backend/requirements.txt
RUN pip install -r requirements.txt

# copy project
COPY . /map-backend/
