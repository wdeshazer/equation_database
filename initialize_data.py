"""Example Script to insert a lot of records
    Useful for testing and development. Shouldn't run in service"""
import os
from random import sample
from equation_group import EquationGroup
from equation import Equation
from variable import Variable

eq_grp = EquationGroup()
eq = Equation()
v = Variable()


grp_count = eq_grp.record_count_total()
eq_count = len(eq.grouped_data)
var_count = len(v.grouped_data)

n = 6 - grp_count
for cnt in range(n):
    eq_grp.insert()

# Safe group id
grp_records = eq_grp.records

# Add upto 15 records and create associations for the newly generated equations
n = 16 - eq_count
for i in range(n):
    eq.new_record()

# Add upto 15 records and create associations for the newly generated equations
n = 25 - var_count
for i in range(n):
    v.new_record()

# Ensure that each group has at least 3 equation records

a_path = os.getcwd() + os.pathsep + 'my_py.py'

for i in range(grp_count):
    grp_id = grp_records[eq_grp.id_name][i]
    eq.set_records_for_parent(parent_id=grp_id)
    used = eq.selected_data_records
    unused = eq.records_not_selected_unique
    eq_count_in_group = len(used)

    # Minimum number of equations in group is 3. The following doesn't loop if eq_count_in_group > 3)
    MAX_EQ_PER_GROUP = 3

    n_unused = len(unused)

    n_more_in_group = MAX_EQ_PER_GROUP - eq_count_in_group
    if n_more_in_group > 0:
        eqns_to_insert = sample(range(1, n_unused), n_more_in_group)
        print(eqns_to_insert)

        for ind in eqns_to_insert:
            child_id = unused[ind].Index
            eq.associate_parent(parent_id=grp_id, child_id=child_id, code_file_path=a_path)

eq_records = eq.all_records
eq_count = len(eq_records)

for i in range(eq_count):
    eq_id = eq_records[eq.id_name][i]
    v.set_records_for_parent(parent_id=eq_id)
    used = v.selected_data_records
    unused = v.records_not_selected_unique
    var_count_in_group = len(used)

    # Minimum number of equations in group is 3. The following doesn't loop if eq_count_in_group > 3)
    MAX_VAR_PER_GROUP = 5

    n_unused = len(unused)

    n_more_in_group = MAX_VAR_PER_GROUP - var_count_in_group
    if n_more_in_group > 0:
        eqns_to_insert = sample(range(1, n_unused), n_more_in_group)
        print(eqns_to_insert)

        for ind in eqns_to_insert:
            child_id = unused[ind].Index
            v.associate_parent(parent_id=eq_id, child_id=child_id)
