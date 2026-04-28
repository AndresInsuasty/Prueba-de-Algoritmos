# Prueba-de-Algoritmos

Repositorio de experimentos y demos de algoritmos.

## Sorting Race (carrera de ordenamientos)

Demo en **Python** con **Pygame** y gestión de dependencias con **uv**: cuatro algoritmos (burbuja, inserción, quicksort y mergesort) compiten ordenando la misma permutación inicial; podés apostar cuál termina primero y ajustar tamaño y velocidad desde la interfaz.

### Requisitos

- [uv](https://docs.astral.sh/uv/) instalado
- Python 3.11+ (lo fija el proyecto)

### Cómo ejecutar

Desde la raíz del repositorio:

```bash
cd Sorting_race
uv sync
uv run sorting-race
```

Alternativas equivalentes:

```bash
cd Sorting_race
uv run python -m sorting_race
```

Opciones de línea de comandos:

```bash
uv run sorting-race --n 128 --seed 42
```

- `--n`: cantidad de barras (entre 2 y 512; también se puede cambiar con los botones del HUD).
- `--seed`: semilla para repetir la misma permutación en otra máquina o clase.

### Controles rápidos

| Acción | Teclado / interfaz |
|--------|---------------------|
| Iniciar carrera | **SPACE** o botón **Iniciar** |
| Nueva permutación | **R** o **Nueva** |
| Apuesta | **1–4** o clic en un cuadrante (en fase apuesta) |
| Tamaño (presets) | **[** / **]** o botones numéricos del HUD |
| Velocidad (pasos por frame) | **+** / **−** o botones **+** / **−** |
| Salir | **ESC** |

### Capturas de pantalla

**Fase de apuesta** — mismos datos en los cuatro cuadrantes; apuesta opcional (ejemplo: Quick seleccionado).

![Fase de apuesta](docs/sorting_race/01-apuesta.png)

**Durante la carrera** — cada algoritmo avanza por pasos; los resaltados muestran comparaciones / pivote según el método.

![Carrera en curso](docs/sorting_race/02-carrera.png)

**Resultado** — orden de llegada y mensaje si la apuesta acertó o no.

![Resultado y ganador](docs/sorting_race/03-resultado.png)

### Regenerar las capturas del README

Si cambiás la interfaz y querés volver a generar los PNG en `docs/sorting_race/`:

```bash
cd Sorting_race
uv run python scripts/capture_readme_screenshots.py
```

Usa el driver de vídeo `dummy` de SDL y no abre ventana.
