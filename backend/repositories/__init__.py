"""
Repositories
Data access layer using repository pattern
"""

from .note_repository import NoteRepository, get_note_repository

__all__ = ['NoteRepository', 'get_note_repository']
