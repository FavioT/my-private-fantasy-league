import sys
import os

# Agregar src/backend al Python path para que funcionen los imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

from app import app
