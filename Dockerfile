# Use an official Python runtime as the base image
FROM python:3.10.9

# Set the working directory in the container to /app
WORKDIR /app

# Copy requirements.txt into the working directory
COPY requirements.txt ./

# Install the bot's dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the bot's code into the working directory
COPY . .

# Start the bot
CMD [ "python", "-u", "ReSubBotMain.py" ]
