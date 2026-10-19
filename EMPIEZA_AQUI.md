# Tu primera sesión

Este es un simulacro de práctica no oficial. Empieza sin cronómetro; los enunciados están en inglés para practicar en condiciones de entrevista.

1. Abre `notebooks/assessment.ipynb` y selecciona el kernel **Python 3 (ipykernel)**.
2. Ejecuta la celda de exploración con **Shift+Enter**. Verás las cuatro tablas disponibles.
3. Lee **Stage 1** en `TASKS.md` y abre `assessment/solution.py` en otra pestaña.
4. Escribe tu implementación de `clean_events`, sustituyendo su `raise NotImplementedError`. Guarda con **Ctrl+S**.
5. Ejecuta la celda de tests de **Stage 01**. También puedes usar la terminal: `python -m pytest -q tests/test_01_clean.py`.
6. Cuando pasen las cuatro pruebas de esa etapa, guarda un commit y sincronízalo con GitHub. Escribe en el chat: «Revisa la etapa 1; dame pistas sin la solución».

Los tests fallan inicialmente porque las funciones están vacías. Un `NotImplementedError` es normal hasta que implementes esa función. Si aparece `ModuleNotFoundError`, espera a que termine la preparación del entorno.

## Progreso

- [ ] Etapa 1: limpieza — 4 tests — 18 min
- [ ] Etapa 2: variables por cliente — 4 tests — 25 min
- [ ] Etapa 3: NumPy — 3 tests — 12 min
- [ ] Etapa 4: modelo y métricas — 3 tests — 30 min
- [ ] Etapa 5: decisión de negocio — 3 tests — 15 min
- [ ] Respuestas razonadas en `ANSWERS.md`

Resuelve en orden: algunas pruebas de las etapas posteriores necesitan las funciones anteriores. Los tests son públicos y no sustituyen una revisión de calidad o de fugas de información.

Para recibir feedback, sincroniza tus cambios. Los archivos sin sincronizar del Codespace no se reciben automáticamente en el chat. Al terminar, detén el Codespace desde el menú de Codespaces para dejar de usar cómputo.
