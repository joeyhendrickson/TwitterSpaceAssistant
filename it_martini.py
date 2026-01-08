# Redirect file for legacy references to it_martini.py
# This file redirects to the main application

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the main application
if __name__ == "__main__":
    # Import the main application
    from main import *
    
    # If running with streamlit, this will automatically start the app
    # If running directly, you can add any additional startup code here
    pass

