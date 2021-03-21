"""Example Script to insert a lot of records
    Useful for testing and development. Shouldn't run in service"""
import os
from random import sample
from pandas import DataFrame
from equation_group import EquationGroup
from equations import GroupedEquations
from variables import GroupedVariables
from latex_data import LatexData

print("Importing Equation Groups")
eq_grp = EquationGroup()
print("Importing Equations")
eq = GroupedEquations()
print("Importing Variables")
v = GroupedVariables()


grp_count = len(eq_grp.all_records)
eq_count = len(eq.grouped_data)
var_count = len(v.grouped_data)

print("Populating Equation Groups")
n = 6 - grp_count
for cnt in range(n):
    eq_grp.new_record()

# Safe group id
grp_records = eq_grp.all_records

# Add upto 15 records and create associations for the newly generated equations
print("Populating Equations")
n = 16 - eq_count
for i in range(n):
    eq.new_record()

# Add upto 15 records and create associations for the newly generated equations
print("Populating Variables")
n = 25 - var_count
for i in range(n):
    v.new_record()

# Ensure that each group has at least 3 equation records

a_path = os.getcwd() + os.pathsep + 'my_py.py'

for grp_id in grp_records.index:
    eq.set_records_for_parent(parent_id=grp_id)
    used = eq.selected_data_records
    unused = eq.records_not_selected_unique
    eq_count_in_group = len(used) if used is not None else 0

    # Minimum number of equations in group is 3. The following doesn't loop if eq_count_in_group > 3)
    MAX_EQ_PER_GROUP = 3

    n_unused = len(unused) if unused is not None else 0

    n_more_in_group = MAX_EQ_PER_GROUP - eq_count_in_group
    if n_more_in_group > 0:
        eqns_to_insert = sample(range(1, n_unused), n_more_in_group)
        print(eqns_to_insert)

        for ind in eqns_to_insert:
            child_id = unused[ind].Index
            print("Associating parent: " + str(grp_id) + ' with: ' + str(child_id))
            eq.associate_parent(parent_id=grp_id, child_id=child_id, code_file_path=a_path)

eq_records: DataFrame = eq.all_records
eq_count = len(eq_records)

for eq_id in eq_records.index:
    v.set_records_for_parent(parent_id=eq_id)
    used = v.selected_data_records
    unused = v.records_not_selected_unique
    var_count_in_group = len(used) if used is not None else 0

    # Minimum number of equations in group is 3. The following doesn't loop if eq_count_in_group > 3)
    MAX_VAR_PER_GROUP = 5

    n_unused = len(unused) if unused is not None else 0

    n_more_in_group = MAX_VAR_PER_GROUP - var_count_in_group
    if n_more_in_group > 0:
        eqns_to_insert = sample(range(1, n_unused), n_more_in_group)
        print(eqns_to_insert)

        for ind in eqns_to_insert:
            child_id = unused[ind].Index
            v.associate_parent(parent_id=eq_id, child_id=child_id)
            print("Associating parent: " + str(eq_id) + ' with: ' + str(child_id))


from unit import Unit
from latex_data import LatexData
un = Unit()

bb_file = open('Icons/big_bang_64x64.jpg', 'rb')
bb_data = bb_file.read()
bb_file.close()

un_ltx = LatexData(latex='the beginning', image=bb_data)

un.update(an_id=1, latex=un_ltx)

# un_file = open('Icons/clipart-green-one-196b.png', 'rb')
# bb_data = bb_file.read()
# bb_file.close()
#
# un_one = LatexData(latex='$1$')
