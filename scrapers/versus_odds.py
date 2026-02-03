"""
Módulo scraper para obtener cuotas de Versus.es (polling).
Frecuencia: Cada 15-20s durante ventana activa.

TODO: Inicializar browser persistente (Playwright)
TODO: Implementar loop de polling para carreras activas (T-10 a T-1)
TODO: Navegar directamente a URL de carrera (usando external_ids)
TODO: Extraer datos de caballos (dorsal, nombre, cuota WIN)
TODO: Parsear cuotas decimales
TODO: Generar timestamp UTC
TODO: Guardar snapshot en tabla odds_snapshots
TODO: Manejar errores de timeout y DOM no encontrado
TODO: Logging de latencia
"""

async def poll_versus_odds(race_id):
    pass
