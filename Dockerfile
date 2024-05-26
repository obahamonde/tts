FROM python:3.11
WORKDIR /app
COPY . .
# install ffmpeg

RUN apt-get update
RUN apt-get install -y ffmpeg
RUN apt-get install -y libsm6 libxext6
RUN apt-get install -y libxrender-dev
RUN apt-get install -y libgl1-mesa-glx

# install python dependencies
RUN pip install --upgrade pip
RUN pip install spacy==3.1.3
RUN pip install -r requirements.txt
RUN pythom -m spacy download en_core_web_sm
RUN python -m spacy download es_core_news_sm
EXPOSE 5000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]