FROM python:3.11
WORKDIR /app
COPY . .
RUN apt-get update && apt-get install -y ffmpeg
EXPOSE 8080
RUN pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]