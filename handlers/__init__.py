from .base import router as base_router
from .specialties import router as specialties_router
from .sections import router as sections_router
from .operator import router as operator_router

# Собираем все роутеры в один список для удобного импорта
__all__ = [
    'base_router',
    'specialties_router',
    'sections_router',
    'operator_router'
]