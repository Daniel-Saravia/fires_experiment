#!/bin/bash

# Check if conda is installed
if ! command -v conda &> /dev/null
then
    echo "conda could not be found. Please install Anaconda or Miniconda first."
    exit
fi

# Create the conda environment from environment.yml located one directory up
echo "Creating conda environment..."
conda env create -f ../environment.yml

# Activate the conda environment
echo "Activating conda environment..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate web_scraper

# Install Nginx
echo "Installing Nginx..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo apt-get update
    sudo apt-get install -y nginx
elif [[ "$OSTYPE" == "darwin"* ]]; then
    brew install nginx
else
    echo "OS not supported for automatic Nginx installation. Please install Nginx manually."
    exit 1
fi

# Start Nginx
echo "Starting Nginx..."
sudo systemctl start nginx

# Configure Nginx (assuming you want to proxy requests to Gunicorn on port 8000)
NGINX_CONF="
server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
"

echo "Configuring Nginx..."
echo "$NGINX_CONF" | sudo tee /etc/nginx/sites-available/web_scraper
sudo ln -s /etc/nginx/sites-available/web_scraper /etc/nginx/sites-enabled/

# Restart Nginx to apply the configuration
echo "Restarting Nginx..."
sudo systemctl restart nginx

# Inform the user that the setup is complete
echo "Setup complete! Nginx is configured to proxy requests to Gunicorn on port 8000."

# Instructions for running the application
echo "To start the application, run the following command:"
echo "gunicorn -w 4 -b 127.0.0.1:8000 app:app"

# End of script