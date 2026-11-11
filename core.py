"""سرور Flask مشترک. داشبوردهای Dash روی همین سرور سوار می‌شوند."""
from flask import Flask

server = Flask(__name__)
