"""
 - For each name part (if full name) or name entry (use tags):
   - Add to Name table
   - aggregate birth year range
   - increase sighting count (if not jmnedict, non-person)
       factoring in real/pen-name/fictional
   - mark as top5k if surname and in myoji-yurai list
   - mark gender (from jmnedict) if specified
"""
from yomikun.loader.aggregator import Aggregator
from yomikun.loader.loader import Loader
