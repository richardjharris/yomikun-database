### yomikun-database

Scripts and modules to generate the name database used by Yomikun.
This includes:

- parsing Wikipedia and other dictionary data
- generating lists such as top 1000 lists
- assembling the data into an SQLite file

## Directory structure

- daijisen - tools for reading Daijisen's epwing data
- reading - classes used by everything else
- scripts - command-line scripts
- tests - wider-scale unit tests
- wikipedia - tools for parsing Wikipedia articles

## Running tests

Just run `pytest` from the module root.
