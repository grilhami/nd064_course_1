FROM python:2.7

WORKDIR /usr/src/app

COPY . .
RUN pip install --upgrade setuptools
RUN pip install --no-cache-dir -r requirements.txt
RUN python init_db.py

EXPOSE 3111

CMD [ "python", "app.py" ]