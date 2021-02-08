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
-- DROP TABLE if EXISTS variable_equation CASCADE;
-- DROP TABLE IF EXISTS equation_type CASCADE;
DROP SCHEMA IF EXISTS schema_templates CASCADE;
DROP SCHEMA IF EXISTS public CASCADE;

CREATE SCHEMA schema_templates;
CREATE SCHEMA public;

-- tables

CREATE TABLE template (
  id BIGSERIAL PRIMARY KEY,
  data text NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by text NOT NULL
);

CREATE TABLE schema_templates.latex_object(
    name TEXT NOT NULL,
    latex TEXT NOT NULL,
    notes text, -- For a more detailed description
    image BYTEA DEFAULT NULL,
    template_id INT,
    image_is_dirty BOOL DEFAULT FALSE, -- Image load inconsistent with last latex load
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by TEXT NOT NULL,
    modified_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    modified_by TEXT NOT NULL,
    compiled_at TIMESTAMPTZ DEFAULT NULL,
    CONSTRAINT math_object_ak_1 UNIQUE (name) NOT DEFERRABLE,
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
    unit_id BIGSERIAL PRIMARY KEY,
    LIKE schema_templates.latex_object INCLUDING ALL,
    type text NOT NULL DEFAULT 'SI',
    CONSTRAINT fk_template
        FOREIGN KEY (type)
            REFERENCES unit_type (type)
);

CREATE TABLE schema_templates.physics_object (
    LIKE schema_templates.latex_object INCLUDING ALL,
    dimensions int DEFAULT NULL,
    unit_id int  NOT NULL,
    CONSTRAINT fk_unit
        FOREIGN KEY(unit_id)
            REFERENCES template(id)
);


-- Reference: Variable_Unit (table: Variable)
ALTER TABLE schema_templates.physics_object ADD CONSTRAINT physics_object_unit
    FOREIGN KEY (unit_id)
    REFERENCES unit (unit_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Table: eqn_group
CREATE TABLE eqn_group (
    eqn_group_id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    notes TEXT, -- For a more detailed description
    created_by TEXT NOT NULL,
    modified_by TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    modified_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT eq_group_name_ak_1 UNIQUE (name) NOT DEFERRABLE
);

CREATE OR REPLACE FUNCTION trigger_eqn_group_insert() RETURNS TRIGGER
    LANGUAGE plpgsql
    AS $$
    BEGIN
        new.modified_at = now();

        if new.modified_by IS NULL THEN
            new.modified_by = new.created_by;
        END IF;

        RETURN new;
    END;
    $$;

CREATE TRIGGER eqn_group_insert
    BEFORE INSERT ON eqn_group
    for EACH ROW
    EXECUTE PROCEDURE trigger_eqn_group_insert();

CREATE OR REPLACE FUNCTION trigger_eqn_group_update() RETURNS TRIGGER
    LANGUAGE plpgsql
    AS $$
    BEGIN
        new.modified_at = now();
        RETURN new;
    END;
    $$;

CREATE TRIGGER eqn_group_modified
    BEFORE UPDATE ON eqn_group
    for EACH ROW
    EXECUTE PROCEDURE trigger_eqn_group_update();


-- Table: equation
CREATE TABLE equation (
    equation_id BIGSERIAL PRIMARY KEY,
    LIKE schema_templates.physics_object INCLUDING ALL,
    type text  NOT NULL,
    associated_code_file text
);

-- Table: Equation_Eqn_Group
CREATE TABLE equation_eqn_group (
    equation_id INT  NOT NULL,
    eqn_group_id INT NOT NULL,
    code_file_path TEXT, -- Each record can have its own code filepath
    insertion_order BIGINT,
    insertion_order_prev BIGINT,
    insertion_date TIMESTAMPTZ NOT NULL DEFAULT now(),
    inserted_by TEXT NOT NULL,
    CONSTRAINT equation_eqn_group_pk PRIMARY KEY (equation_id,eqn_group_id)
);

-- foreign keys
-- Reference: Equation_Eqn_Group_Eqn_Group (table: Equation_Eqn_Group)
ALTER TABLE equation_eqn_group ADD CONSTRAINT equation_eqn_group_fk_eqn_group_id
    FOREIGN KEY (eqn_group_id)
    REFERENCES eqn_group (eqn_group_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: Equation_Eqn_Group_Equation (table: Equation_Eqn_Group)
ALTER TABLE equation_eqn_group ADD CONSTRAINT equation_eqn_group_fk_equation_id
    FOREIGN KEY (equation_id)
    REFERENCES Equation (equation_id)
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
    ('Correlation'),
    ('Equality');


-- Reference: Equation_Equation_Type (table: Equation)
ALTER TABLE equation ADD CONSTRAINT equation_fk_equation_typ
    FOREIGN KEY (type)
    REFERENCES equation_type (type)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Table: Variable
CREATE TABLE variable (
    variable_id BIGSERIAL PRIMARY KEY,
    LIKE schema_templates.physics_object INCLUDING ALL,
    variable_type text NOT NULL
);

-- Table: Equation_Type
CREATE TABLE variable_type (
    type text  PRIMARY KEY
);

INSERT INTO variable_type (type)
VALUES
    ('Constant'),
    ('Coordinate'),
    ('Field');

-- Table: variable_equation
CREATE TABLE variable_equation (
    variable_id int8  NOT NULL,
    equation_Id int8  NOT NULL,
    insertion_order BIGINT,
    insertion_order_prev BIGINT,
    insertion_date TIMESTAMPTZ NOT NULL DEFAULT now(),
    inserted_by TEXT NOT NULL,
    CONSTRAINT variable_equation_pk PRIMARY KEY (variable_id,equation_id)
);

-- Reference: variable_equation_Equation (table: variable_equation)
ALTER TABLE variable_equation ADD CONSTRAINT variable_equation_fk_equation_id
    FOREIGN KEY (equation_id)
    REFERENCES equation (equation_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: variable_equation_Variable (table: variable_equation)
ALTER TABLE variable_equation ADD CONSTRAINT variable_equation_fk_variable_id
    FOREIGN KEY (variable_id)
    REFERENCES variable (variable_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Functions

do $$
    DECLARE
        file_location VARCHAR(100) := '/mnt/c/Users/earld/Documents/Fusion/equation_database/LaTeX/eq_template.tex';
    BEGIN
        INSERT INTO template (data, created_by) VALUES (pg_read_file(file_location), 'Will DeShazer');
    END
    $$;

CREATE OR REPLACE FUNCTION trigger_copy_previous_insertion_order() RETURNS TRIGGER
    LANGUAGE plpgsql
    AS $$
    BEGIN
        new.insertion_order_prev := old.insertion_order;
        RETURN new;
    END;
    $$;

CREATE TRIGGER update_eqn_order
    BEFORE UPDATE ON equation_eqn_group
    for EACH ROW
    EXECUTE PROCEDURE trigger_copy_previous_insertion_order();

CREATE TRIGGER update_var_order
    BEFORE UPDATE ON variable_equation
    for EACH ROW
    EXECUTE PROCEDURE trigger_copy_previous_insertion_order();


CREATE OR REPLACE FUNCTION trigger_insertion_order_eqn() RETURNS TRIGGER
    LANGUAGE plpgsql
    AS $$
    DECLARE
        the_count integer;
    BEGIN
        if new.insertion_order is NULL then
            SELECT INTO the_count COUNT(equation_id) FROM equation_eqn_group WHERE eqn_group_id = new.eqn_group_id;
            new.insertion_order = the_count + 1;
            new.insertion_order_prev := the_count + 1;
        end if;
        RETURN new;
    END;
    $$;

CREATE TRIGGER insert_eqn_order
    BEFORE INSERT ON equation_eqn_group
    for EACH ROW
    EXECUTE PROCEDURE trigger_insertion_order_eqn();

CREATE OR REPLACE FUNCTION trigger_insertion_order_var() RETURNS TRIGGER
    LANGUAGE plpgsql
    AS $$
    DECLARE
        the_count integer;
    BEGIN
        if new.insertion_order is NULL then
            SELECT INTO the_count COUNT(variable_id) FROM variable_equation WHERE equation_id = new.equation_id;
            new.insertion_order = the_count + 1;
            new.insertion_order_prev := the_count + 1;
        end if;
        RETURN new;
    END;
    $$;

CREATE TRIGGER insert_var_order
    BEFORE INSERT ON variable_equation
    for EACH ROW
    EXECUTE PROCEDURE trigger_insertion_order_var();


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
        new.template_id = (SELECT id FROM template ORDER BY created_at DESC FETCH FIRST ROW ONLY);
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

CREATE OR REPLACE FUNCTION trigger_insert() RETURNS TRIGGER
    LANGUAGE plpgsql
    AS $$
    BEGIN

        IF new.image IS NOT NULL THEN
            new.compiled_at = now();
        END IF;

        IF new.modified_by IS NULL THEN
            new.modified_by = new.created_by;
        END IF;

        RETURN new;
    END;
    $$;

CREATE TRIGGER latex_compiled
    BEFORE INSERT ON equation
    for EACH ROW
    EXECUTE PROCEDURE trigger_insert();

CREATE TRIGGER latex_compiled
    BEFORE INSERT ON variable
    for EACH ROW
    EXECUTE PROCEDURE trigger_insert();

CREATE TRIGGER latex_compiled
    BEFORE INSERT ON unit
    for EACH ROW
    EXECUTE PROCEDURE trigger_insert();


CREATE OR REPLACE FUNCTION trigger_set_update() RETURNS TRIGGER
    LANGUAGE plpgsql
    AS $$
    BEGIN
        new.modified_at = now();

        IF new.image IS NOT NULL THEN
            new.compiled_at = now();
        END IF;

        IF new.latex IS NOT NULL and new.image IS NULL THEN
            new.image_is_dirty = TRUE;
        END IF;

        RETURN new;
    END;
    $$;

CREATE TRIGGER modified_by_on_insert
    BEFORE UPDATE ON equation
    for EACH ROW
    EXECUTE PROCEDURE trigger_set_update();

CREATE TRIGGER modified_by_on_insert
    BEFORE UPDATE ON variable
    for EACH ROW
    EXECUTE PROCEDURE trigger_set_update();

CREATE TRIGGER modified_by_on_insert
    BEFORE UPDATE ON unit
    for EACH ROW
    EXECUTE PROCEDURE trigger_set_update();

-- noinspection SqlInsertValues

INSERT INTO unit (name, latex, created_by)
VALUES
    ('Unitless', '', 'razor'),
    ('meter', 'm', 'razor');

