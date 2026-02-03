"""
Definición de modelos SQLAlchemy.

TODO: Definir Base = declarative_base()
TODO: Modelo Bookmaker (id, name, type, country)
TODO: Modelo TrackAlias (canonical, alias, bookmaker_id)
TODO: Modelo Meeting (id, track, country, date)
TODO: Modelo Race (id, meeting_id, number, time, status)
TODO: Modelo Runner (id, race_id, name, saddle)
TODO: Modelo OddsSnapshot (runner_id, odds, timestamp)
TODO: Modelo ValueBet (race_id, runner_id, edge, status)
"""

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
