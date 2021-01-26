DB_TABLE_NAMES_Q = """SELECT table_name 
    FROM information_schema.tables
    WHERE table_schema = 'public'"""


