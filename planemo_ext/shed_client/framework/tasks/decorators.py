"""
"""

try:
    from celery import shared_task
except ImportError:
    from .compat import shared_task


__all__ = ['shared_task']
