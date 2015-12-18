"""
"""
try:
    from celery import Celery
except ImportError:
    Celery = None
