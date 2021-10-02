"""
Takes these inputs:
 1) deduped Person data
 2) deduped Name data (various name parts)
 3) gender dictionary
 4) gender ML model

Produces data in a format suitable for database load:
Name:
 ID, kaki, yomi, pos (sei/mei/unclas), male_people, female_people, total_people, gender_score, ml_gender_score,
   from_year, to_year, normalised_romaji, confidence

 (confidence is based on count of people + whether those people are fictional or pen-names)
 (where kaki='*', yomi=kana, stats are aggregated for all uses of a particular yomi (regardless of written
  style)

People:
 sei (ID), mei (ID), birth_year, death_year, gender, authenticity (fictional/pseudo/real), sources
"""
