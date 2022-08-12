FROM python:3.10

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt requirements.txt
# Install requirements
# RUN pip install pip-tools && pip-compile && cat requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "-m", "app.main"]
