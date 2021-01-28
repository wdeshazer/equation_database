-- Created by Vertabelo (http://vertabelo.com)
-- Last modification date: 2020-12-16 03:55:40.497

-- tables
-- Table: Eqn_Group
CREATE TABLE Eqn_Group (
    Eqn_Group_ID int  NOT NULL,
    Eqn_Group_Name varchar(50)  NOT NULL,
    Create_by varchar(50)  NOT NULL,
    Create_date timestamp  NOT NULL,
    CONSTRAINT Eqn_Group_ak_1 UNIQUE (Eqn_Group_Name) NOT DEFERRABLE  INITIALLY IMMEDIATE,
    CONSTRAINT Eqn_Group_pk PRIMARY KEY (Eqn_Group_ID)
);

-- Table: Equation
CREATE TABLE Equation (
    Equation_Id bigserial  NOT NULL,
    Equation_Name varchar(50)  NOT NULL,
    Equation_Latex text  NOT NULL,
    Equation_image bytea  NOT NULL,
    Equation_thumbnail bytea  NOT NULL,
    Equation_type_id int  NOT NULL,
    uom_id int  NOT NULL,
    Create_by varchar(50)  NOT NULL,
    Create_date timestamp  NOT NULL,
    Last_changed_by varchar(50)  NOT NULL,
    Last_changed_date timestamp  NOT NULL,
    CONSTRAINT Equation_ak_1 UNIQUE (Equation_Name) NOT DEFERRABLE  INITIALLY IMMEDIATE,
    CONSTRAINT Equation_pk PRIMARY KEY (Equation_Id)
);

-- Table: Equation_Eqn_Group
CREATE TABLE Equation_Eqn_Group (
    Eqn_Group_ID int  NOT NULL,
    Equation_Id int8  NOT NULL,
    insertion_date timestamp  NOT NULL,
    CONSTRAINT Equation_Eqn_Group_pk PRIMARY KEY (Eqn_Group_ID,Equation_Id)
);

-- Table: Equation_Type
CREATE TABLE Equation_Type (
    equation_type_id int  NOT NULL,
    equation_type_name varchar(50)  NOT NULL,
    CONSTRAINT Equation_Type_ak_1 UNIQUE (equation_type_name) NOT DEFERRABLE  INITIALLY IMMEDIATE,
    CONSTRAINT Equation_Type_pk PRIMARY KEY (equation_type_id)
);

-- Table: Equation_Variable
CREATE TABLE Equation_Variable (
    Variables_id int8  NOT NULL,
    Equation_Id int8  NOT NULL,
    CONSTRAINT Equation_Variable_pk PRIMARY KEY (Variables_id,Equation_Id)
);

-- Table: Unit_of_Measure
CREATE TABLE Unit_of_Measure (
    uom_id int  NOT NULL,
    uom_name varchar(50)  NOT NULL,
    uom_type varchar(20)  NOT NULL,
    CONSTRAINT Unit_of_Measure_ak_1 UNIQUE (uom_name) NOT DEFERRABLE  INITIALLY IMMEDIATE,
    CONSTRAINT Unit_of_Measure_pk PRIMARY KEY (uom_id)
);

-- Table: Variable
CREATE TABLE Variable (
    variables_id bigserial  NOT NULL,
    variable_name varchar(50)  NOT NULL,
    variable_latex text  NOT NULL,
    variable_image bytea  NOT NULL,
    variable_thumbnail bytea  NOT NULL,
    uom_id int  NOT NULL,
    CONSTRAINT Variable_ak_1 UNIQUE (variable_name) NOT DEFERRABLE  INITIALLY IMMEDIATE,
    CONSTRAINT Variable_pk PRIMARY KEY (variables_id)
);

-- foreign keys
-- Reference: Equation_Eqn_Group_Eqn_Group (table: Equation_Eqn_Group)
ALTER TABLE Equation_Eqn_Group ADD CONSTRAINT Equation_Eqn_Group_Eqn_Group
    FOREIGN KEY (Eqn_Group_ID)
    REFERENCES Eqn_Group (Eqn_Group_ID)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: Equation_Eqn_Group_Equation (table: Equation_Eqn_Group)
ALTER TABLE Equation_Eqn_Group ADD CONSTRAINT Equation_Eqn_Group_Equation
    FOREIGN KEY (Equation_Id)
    REFERENCES Equation (Equation_Id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: Equation_Equation_Type (table: Equation)
ALTER TABLE Equation ADD CONSTRAINT Equation_Equation_Type
    FOREIGN KEY (Equation_type_id)
    REFERENCES Equation_Type (equation_type_id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: Equation_UOM (table: Equation)
ALTER TABLE Equation ADD CONSTRAINT Equation_UOM
    FOREIGN KEY (uom_id)
    REFERENCES Unit_of_Measure (uom_id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: Equation_Variable_Equation (table: Equation_Variable)
ALTER TABLE Equation_Variable ADD CONSTRAINT Equation_Variable_Equation
    FOREIGN KEY (Equation_Id)
    REFERENCES Equation (Equation_Id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: Equation_Variable_Variable (table: Equation_Variable)
ALTER TABLE Equation_Variable ADD CONSTRAINT Equation_Variable_Variable
    FOREIGN KEY (Variables_id)
    REFERENCES Variable (variables_id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: Variable_UOM (table: Variable)
ALTER TABLE Variable ADD CONSTRAINT Variable_UOM
    FOREIGN KEY (uom_id)
    REFERENCES Unit_of_Measure (uom_id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- sequences
-- Sequence: EqnGroup_Seq
CREATE SEQUENCE EqnGroup_Seq
      INCREMENT BY 1
      NO MINVALUE
      NO MAXVALUE
      START WITH 1
      NO CYCLE
;

-- Sequence: Equation_Seq
CREATE SEQUENCE Equation_Seq
      INCREMENT BY 1
      NO MINVALUE
      NO MAXVALUE
      START WITH 1
      NO CYCLE
;

-- Sequence: UOM_Seq
CREATE SEQUENCE UOM_Seq
      INCREMENT BY 1
      NO MINVALUE
      NO MAXVALUE
      START WITH 1
      NO CYCLE
;

-- Sequence: Variable_seq
CREATE SEQUENCE Variable_seq
      INCREMENT BY 1
      NO MINVALUE
      NO MAXVALUE
      START WITH 1
      NO CYCLE
;

-- End of file.

