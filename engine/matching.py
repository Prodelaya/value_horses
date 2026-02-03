"""
Módulo para emparejar carreras y caballos entre fuentes.

TODO: Implementar match_race(versus_race, teletrak_races)
  - Usar track_aliases para normalizar nombres
  - Comparar fechas y tolerancia de hora (+- 5 min)
  
TODO: Implementar match_horse(versus_name, teletrak_runners)
  - Normalizar strings (quitar acentos, uppercase)
  - Fuzzy matching con Levenshtein (threshold > 90)
  - Guardar map de name_normalized en BD
"""

def match_race(source_race, candidates):
    pass

def match_runner(source_runner, candidates):
    pass
