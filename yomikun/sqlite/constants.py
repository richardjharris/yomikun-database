# Mapping of namedata part names to their IDs. This is done as SQLite
# does not support enums.

PART_ID = {
    "unknown": 0,
    "sei": 1,
    "mei": 2,
    "person": 3,
}

PARTS_IN_DATABASE_ORDER = list(PART_ID.keys())
