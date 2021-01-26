-- QUERY for all Table Names
-- SELECT table_name
-- FROM information_schema.tables
-- WHERE table_schema = 'public'
-- ORDER BY table_name;

DO $$
    BEGIN
        IF EXISTS
            ( SELECT 1
              FROM   information_schema.tables
              WHERE  table_schema = 'public'
              AND    table_name = 'equation'
            )
        THEN
        INSERT INTO unit (name, latex, notes,) VALUES
        ('');
        END IF ;
    END
   $$;

DO $$
    BEGIN
        IF EXISTS
            ( SELECT 1
              FROM   information_schema.tables
              WHERE  table_schema = 'public'
              AND    table_name = 'equation'
            )
        THEN
        INSERT INTO equation (name, latex, image, created_by) VALUES (
            'Mass-Energy',
            'E = m\,c^2',
            pg_read_binary_file('/mnt/c/Users/earld/Documents/Fusion/equation_database/mass_energy.png'),
            'Will DeShazer'
        );
        END IF ;
    END
   $$