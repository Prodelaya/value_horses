"""
Módulo scraper para obtener cuotas de Teletrak.cl (polling).
Frecuencia: Cada 10-15s durante ventana activa.

TODO: Inicializar browser persistente (Playwright)
TODO: Implementar loop de polling para carreras activas
TODO: Navegar a /wager?raceCardId=X&raceId=Y
TODO: Verificar que pestaña "Apuesta" esté activa
TODO: Extraer tabla de caballos (No., Nombre, Prob)
TODO: Parsear cuota Prob (convertir coma a punto, quitar 'FAV')
TODO: Guardar snapshot en tabla odds_snapshots
TODO: Manejar errores de navegación o carga lenta
TODO: Logging de latencia y volumen de datos
"""

async def poll_teletrak_odds(race_id):
    pass
