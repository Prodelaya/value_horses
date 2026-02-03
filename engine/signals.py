"""
Módulo para generación y envío de señales (value bets).

TODO: Implementar check_for_value(race_id)
  - Obtener últimos snapshots de sharp y soft
  - Calcular p_fair y edge
  - Si edge > MIN_EDGE, crear ValueBet en BD
  
TODO: Implementar send_alert(value_bet)
  - Formatear mensaje (Track, Caballo, Cuota, Edge)
  - Integración futura con Telegram/Discord
  - Marcar bet como 'SENT' en BD
"""

def process_race_signals(race_id):
    pass
