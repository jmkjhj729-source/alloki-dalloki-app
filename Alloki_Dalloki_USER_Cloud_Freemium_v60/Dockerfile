FROM python:3.11-slim

WORKDIR /app
COPY . /app

# Install deps
RUN pip install --no-cache-dir -r requirements_user.txt

# Streamlit config
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

EXPOSE 8501
CMD ["streamlit", "run", "ui_streamlit.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
