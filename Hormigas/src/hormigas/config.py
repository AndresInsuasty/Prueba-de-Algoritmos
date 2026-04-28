from __future__ import annotations

# Ventana y grilla
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
HUD_HEIGHT = 182
CELL = 16

# Tamaño de la grilla (se calcula en main según el área útil; aquí valores por defecto)
DEFAULT_GRID_W = 72
DEFAULT_GRID_H = 38

FPS = 60
ANT_COUNT = 36

# ACO / feromonas (valores por defecto equilibrados para la demo en clase)
RHO = 0.01
TAU0 = 0.12
ALPHA = 1.45
Q_DEPOSIT = 1.0
PHERO_CAP = 18.0
FOOD_PER_CLICK = 4.0
NEST_RADIUS = 2

# Colores
COLOR_BG = (24, 28, 32)
COLOR_HUD = (32, 36, 44)
COLOR_TEXT = (230, 232, 238)
COLOR_MUTED = (150, 155, 170)
COLOR_WALL = (42, 130, 235)
COLOR_FLOOR = (42, 46, 54)
COLOR_NEST = (120, 90, 60)
COLOR_FOOD = (60, 200, 90)
COLOR_FOOD_CORE = (140, 255, 120)
COLOR_ANT_SEARCH = (220, 200, 80)
COLOR_ANT_RETURN = (255, 140, 90)
COLOR_PHERO = (180, 80, 200)
COLOR_BTN = (48, 52, 72)
COLOR_BTN_BORDER = (85, 92, 118)
COLOR_BTN_ACTIVE = (70, 110, 175)
COLOR_BTN_DISABLED = (38, 38, 48)
COLOR_BTN_TEXT = (220, 222, 230)
