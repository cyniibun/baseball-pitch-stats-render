#game_view.py
import sys
import os

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# scripts/preload_schedule.py
from utils.schedule_utils import preload_upcoming_days

# Preload schedules for today and tomorrow
preload_upcoming_days(days=2)