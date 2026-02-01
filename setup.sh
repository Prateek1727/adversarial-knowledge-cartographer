#!/bin/bash

echo "Setting up Adversarial Knowledge Cartographer..."
echo

echo "Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "Failed to create virtual environment"
    exit 1
fi

echo
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment"
    exit 1
fi

echo
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install dependencies"
    exit 1
fi

echo
echo "Setup complete!"
echo
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo
echo "To run tests, use:"
echo "  pytest"
echo
echo "Don't forget to copy .env.example to .env and add your API keys!"
