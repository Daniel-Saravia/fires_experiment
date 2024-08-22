#!/bin/bash

# Ensure the conda command is available by sourcing the correct file
source ~/miniconda3/etc/profile.d/conda.sh  # Adjust the path if necessary

# Activate the Conda environment
conda activate web_scraper

# Run the scraper
python scraper.py

# Run the Flask application
python app.py

# Deactivate the Conda environment
conda deactivate