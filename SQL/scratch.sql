SELECT * FROM equation;

INSERT INTO equation_eqn_group (equation_id, eqn_group_id, code_file_path,
                                insertion_order, insertion_order_prev, inserted_by)
        VALUES (1, 1, 'some_path', 1, 1, 'razor'),
               (2, 1, 'another_path', 2, 2, 'razor'),
               (5, 1, 'dumb', 3, 3, 'razor'),
               (2, 2, 'dumb', 1, 1, 'razor'),
               (6, 2, 'dumb', 2, 2, 'razor'),
               (4, 2, 'dumb', 3, 3, 'razor');

SELECT * FROM equation_eqn_group RIGHT JOIN equation USING(equation_id) WHERE eqn_group_id = 1;

SELECT equation_id FROM equation_eqn_group WHERE eqn_group_id = 1;

SELECT * FROM equation WHERE equation_id NOT IN (SELECT equation_id FROM equation_eqn_group WHERE eqn_group_id = 1);

-- All Variables for equations in equation group
SELECT * FROM variable JOIN variable_equation ve USING(variable_id)
    JOIN equation_eqn_group eeg USING(equation_id) WHERE eeg.eqn_group_id = 1;

-- All Variables for equations in equation group without duplicate variables
SELECT DISTINCT ON (v.variable_id) * FROM variable v JOIN variable_equation ve USING(variable_id)
