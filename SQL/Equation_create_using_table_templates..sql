-- Created by Will DeShazer
-- Last modification date: 2020-12-23 09:40.20
-- L

-- Cleanup & Prep
-- DROP TABLE if EXISTS template CASCADE;
-- DROP TABLE if EXISTS math_object CASCADE;
-- DROP TABLE if EXISTS equation CASCADE;
-- DROP TABLE if EXISTS eqn_group CASCADE;
-- DROP TABLE if EXISTS equation_eqn_group CASCADE;
-- DROP TABLE if EXISTS variable CASCADE;
-- DROP TABLE if EXISTS equation_variable CASCADE;
-- DROP TABLE IF EXISTS equation_type CASCADE;
DROP SCHEMA IF EXISTS schema_templates CASCADE;
DROP SCHEMA IF EXISTS public CASCADE;

CREATE SCHEMA schema_templates;
CREATE SCHEMA public;

-- tables

CREATE TABLE template (
  id BIGSERIAL PRIMARY KEY,
  data text NOT NULL,
  create_date TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by text NOT NULL
);

CREATE TABLE schema_templates.latex_object(
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    latex TEXT NOT NULL,
    notes text, -- For a more detailed description
    image BYTEA DEFAULT NULL,
    template_id INT,
    table_order BIGINT,
    table_order_prev BIGINT,
    create_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    modified_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by TEXT NOT NULL,
    compiled_at TIMESTAMPTZ DEFAULT NULL,
    CONSTRAINT math_object_ak_1 UNIQUE (name) NOT DEFERRABLE,
    CONSTRAINT table_order_ak_1 UNIQUE (table_order) NOT DEFERRABLE,
    CONSTRAINT table_order_prev_ak_1 UNIQUE (table_order_prev) NOT DEFERRABLE,
    CONSTRAINT fk_template
        FOREIGN KEY(template_id)
            REFERENCES template(id)
);

CREATE TABLE unit_type (
    type text PRIMARY KEY
);

INSERT INTO unit_type (type)
VALUES
    ('SI'),
    ('CGS'),
    ('USCS');

-- Table: Unit
CREATE TABLE unit (
    LIKE schema_templates.latex_object INCLUDING ALL,
    type text NOT NULL DEFAULT 'SI',
    CONSTRAINT fk_template
        FOREIGN KEY (type)
            REFERENCES unit_type (type)
);

INSERT INTO unit (name, latex, table_order, table_order_prev, created_by)
VALUES
    ('Unitless', '', 1, 1, 'razor'),
    ('meter', 'm', 2, 2, 'razor');

CREATE TABLE schema_templates.physics_object (
    LIKE schema_templates.latex_object INCLUDING ALL,
    unit_id int  NOT NULL,
    CONSTRAINT fk_unit
        FOREIGN KEY(unit_id)
            REFERENCES template(id)
);


-- Reference: Variable_Unit (table: Variable)
ALTER TABLE schema_templates.physics_object ADD CONSTRAINT physics_object_unit
    FOREIGN KEY (unit_id)
    REFERENCES unit (id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Table: eqn_group
CREATE TABLE eqn_group (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    notes TEXT, -- For a more detailed description
    created_by TEXT NOT NULL,
    create_date TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT eq_group_name_ak_1 UNIQUE (name) NOT DEFERRABLE
);

-- Table: equation
CREATE TABLE equation (
    LIKE schema_templates.physics_object INCLUDING ALL,
    equation_type text  NOT NULL,
    associated_code_file text
);

-- Table: Equation_Eqn_Group
CREATE TABLE equation_eqn_group (
    equation_id INT  NOT NULL,
    eqn_group_id INT NOT NULL,
    insertion_order BIGINT,
    insertion_order_prev BIGINT,
    insertion_date TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT equation_eqn_group_pk PRIMARY KEY (equation_id,eqn_group_id)
);

-- foreign keys
-- Reference: Equation_Eqn_Group_Eqn_Group (table: Equation_Eqn_Group)
ALTER TABLE equation_eqn_group ADD CONSTRAINT equation_eqn_group_eqn_group
    FOREIGN KEY (eqn_group_id)
    REFERENCES eqn_group (id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: Equation_Eqn_Group_Equation (table: Equation_Eqn_Group)
ALTER TABLE equation_eqn_group ADD CONSTRAINT equation_eqn_group_equation
    FOREIGN KEY (equation_id)
    REFERENCES Equation (id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Table: Equation_Type
CREATE TABLE equation_type (
    type text  PRIMARY KEY
);

INSERT INTO equation_type (type)
VALUES
    ('Conservation'),
    ('Constitutive'),
    ('Definition'),
    ('Corration'),
    ('Equality');


-- Reference: Equation_Equation_Type (table: Equation)
ALTER TABLE equation ADD CONSTRAINT equation_equation_type
    FOREIGN KEY (equation_type)
    REFERENCES equation_type (type)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Table: Variable
CREATE TABLE variable (
    LIKE schema_templates.physics_object INCLUDING ALL
);

-- Table: Equation_Variable
CREATE TABLE equation_variable (
    variables_id int8  NOT NULL,
    equation_Id int8  NOT NULL,
    CONSTRAINT equation_variable_pk PRIMARY KEY (variables_id,equation_id)
);

-- Reference: Equation_Variable_Equation (table: Equation_Variable)
ALTER TABLE equation_variable ADD CONSTRAINT equation_variable_equation
    FOREIGN KEY (equation_id)
    REFERENCES equation (id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: Equation_Variable_Variable (table: Equation_Variable)
ALTER TABLE equation_variable ADD CONSTRAINT equation_variable_variable
    FOREIGN KEY (variables_id)
    REFERENCES variable (id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Functions

CREATE OR REPLACE FUNCTION trigger_set_timestamp() RETURNS TRIGGER
    LANGUAGE plpgsql
    AS $$
    BEGIN
        new.modified_at = now();
        RETURN new;
    END;
    $$;

CREATE TRIGGER latex_compiled
    BEFORE UPDATE ON equation
    for EACH ROW
    EXECUTE PROCEDURE trigger_set_timestamp();

do $$
    DECLARE
        file_location VARCHAR(100) := '/mnt/c/Users/earld/Documents/Fusion/equation_database/LaTeX/eq_template.tex';
    BEGIN
        INSERT INTO template (data, created_by) VALUES (pg_read_file(file_location), 'Will DeShazer');
    END
    $$;

-- do $$
--     BEGIN
--         INSERT INTO latex (data, insert_order, created_by) VALUES (
--         '\cfrac{1}{r} \diffpfunc{ r \func{\hat{\Gamma}_{r\sigma}}{r}}{r} =
-- 			S_{n\sigma} -\diffpfunc{ \FrIOL{\sigma} }{r} \flux{\sigma}',
--         1,
--         'Will DeShazer'
--         );
--     END;
--     $$;

CREATE OR REPLACE FUNCTION template_default()
RETURNS TRIGGER
AS $$ BEGIN
    IF new.template_id IS NULL THEN
        new.template_id = (SELECT id FROM template ORDER BY create_date DESC FETCH FIRST ROW ONLY);
    END IF;
    RETURN new;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER
    template_default
BEFORE INSERT ON
    equation
FOR EACH ROW EXECUTE PROCEDURE
    template_default();


