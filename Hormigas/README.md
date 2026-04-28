# Hormigas — feromonas y comida

Demo en **Pygame** para introducir ideas de colonias de hormigas y **ACO** (versión didáctica): muchas hormigas autónomas, sin coordinador central, exploran una grilla, encuentran comida y refuerzan caminos útiles con **feromonas** que se evaporan.

Al arrancar la simulación está **en pausa**: configurá ρ, α, Q, cantidad de hormigas y velocidad con los botones **− / +**, dibujá muros o añadí comida, y pulsá **Iniciar**. Durante la simulación podés **Pausar**, cambiar la **velocidad** (pasos por frame), ver u ocultar feromonas, limpiar feromonas o **Reiniciar** todo el escenario.

## Ejecutar

```bash
cd Hormigas
uv sync
uv run hormigas
```

Opciones:

```bash
uv run hormigas --ants 64 --seed 7
```

También:

```bash
uv run python -m hormigas
```

## Qué hace el modelo (simplificado para aula)

1. **Nido** (zona marrón): las hormigas nacen ahí y vuelven para “entregar” la comida.
2. **Forrajeo**: en cada paso eligen una celda vecina (8 direcciones) con una **ruleta probabilística**: más feromona ⇒ más probabilidad; hay **ruido** para seguir explorando; si huelen comida en un vecino, se sesga fuerte hacia allí.
3. **Regreso**: al encontrar comida, vuelven al nido **siguiendo la memoria del camino** y, al hacerlo, **depositan feromona** en las celdas por las que pasan.
4. **Evaporación**: cada fotograma las feromonas se atenúan; los malos caminos se olvidan con el tiempo si no se reutilizan.

Sirve para hablar de **heurística**, **estigmergia** (indirecta vía el medio), **exploración vs explotación** y **robustez** frente a obstáculos que dibujás en vivo.

## Controles (interfaz + teclado)

| Elemento | Acción |
|----------|--------|
| **Iniciar / Pausar** | Arranca o detiene la simulación (también **SPACE**). |
| **Reiniciar** | Borra muros, feromonas y comida, vuelve a sembrar comida y hormigas (**R**). |
| **Ferom. on/off** | Muestra u oculta la capa de feromonas (**P**). |
| **Limpiar ferom.** | Pone a cero las feromonas sin borrar muros ni comida (**C**). |
| **Muros / Comida** | Modo de pintado (también **M** para alternar). |
| **− / +** (fila inferior) | Ajustan **ρ** (evaporación), **α** (sensibilidad a feromonas), **Q** (depósito), **velocidad** y **número de hormigas** (solo con la simulación **en pausa**, salvo velocidad). |
| **Ratón en la grilla** | Arrastrar **izquierda**: muros · **derecha**: borrar muros · modo **Comida** + clic: más comida. |
| **G** | Comida aleatoria extra. |
| **ESC** | Salir. |

## Estructura del código

- `config.py` — parámetros visuales y de simulación.
- `world.py` — grilla: muros, feromonas, comida.
- `ants.py` — lógica de cada hormiga.
- `main.py` — bucle Pygame, ratón y teclado.
- `draw.py` — renderizado.
