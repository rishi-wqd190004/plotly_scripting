# Use official lightweight Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy files into container
COPY . .

# Set PYTHONPATH so figure_fridays can be imported
ENV PYTHONPATH=/app

# Install dependencies
RUN pip install --no-cache-dir -r figure_fridays/week_21/app/requirements.txt

# Expose Dash port
EXPOSE 8050

# Start the Dash app with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8050", "figure_fridays.week_21.app.main:server"]
