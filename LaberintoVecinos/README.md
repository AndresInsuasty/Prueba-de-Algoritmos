# Laberinto de los vecinos (BFS vs DFS)

Demo en **Pygame** para comparar **Breadth-First Search** y **Depth-First Search** sobre el **mismo** laberinto: dos paneles lado a lado, celdas visitadas y frontera con colores distintos, y contadores de “pintura” (visitados) para hablar de **memoria** y **optimalidad de camino**.

## Ejecutar

```bash
cd LaberintoVecinos
uv sync
uv run laberinto-vecinos
```

Opción:

```bash
uv run python -m laberinto_vecinos --seed 42
```

## Uso rápido

1. **Editá** el laberinto: clic izquierdo = muro, clic derecho = borrar (solo con la simulación detenida y sin una búsqueda a medias; si quedó a medias, **Reiniciar búsqueda**).
2. Pulsá **Play** (o **SPACE**) para ver **BFS** y **DFS** avanzar a la vez (misma cantidad de pasos lógicos por fotograma configurable).
3. **Pausar** para analizar el estado.
4. **Laberinto aleatorio** o **Vaciar interior** regeneran el mapa (solo en modo edición).

## Idea pedagógica

- **BFS** expande en “olas”; encuentra el **camino más corto** en número de pasos (grafo no ponderado), pero suele marcar **más celdas** hasta llegar a la meta.
- **DFS** “se mete” por un camino; la **frontera** es la pila (normalmente más chica en cantidad de nodos abiertos), pero el camino hallado **no tiene por qué ser el más corto**.

## Archivos

- `config.py` — tamaños y colores.
- `maze.py` — grilla, generación por **recursive backtracker**, vaciar interior.
- `search.py` — generadores `bfs_gen` y `dfs_gen` (un `yield` por paso lógico).
- `draw.py` — HUD con botones y dos paneles.
- `main.py` — bucle Pygame y entrada.

## Capturas para el README del repo

```bash
cd LaberintoVecinos
uv run python scripts/capture_readme_screenshots.py
```

Genera PNG en `docs/laberinto_vecinos/` (driver SDL `dummy`).
