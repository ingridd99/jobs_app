#Starting from an official Python 3.11 image 
FROM python:3.11

#setting the working diractory from the container
WORKDIR /app

#copying the requirements.txt in the container
COPY requirements.txt .

#install the dependencies from the requirements.txt file
RUN pip install -r requirements.txt

#copying the whole project in container
COPY . .

#Command that starts the app when the container is launched?
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]