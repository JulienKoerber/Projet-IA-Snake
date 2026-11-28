import sys
import os

# Ajout du répertoire courant au PYTHONPATH pour PythonAnywhere
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.insert(0, path)

from app import app as application
