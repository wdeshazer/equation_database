"""Example Script to insert a lot of records
    Useful for testing and development. Shouldn't run in service"""
from random import randint, sample
from equation_group import EquationGroup
from equation import Equation
from variable import Variable

eq_grp = EquationGroup()
eq = Equation()
v = Variable()


grp_count = eq_grp.record_count_total()
eq_count = eq.record_count_total()
var_count = v.record_count_total()

n = 6 - grp_count
for cnt in range(n):
    eq_grp.insert()

# Safe group id
grp_records = eq_grp.records

# Add upto 15 records and create associations for the newly generated equations
n = 16 - eq_count
for i in range(n):
    eq.insert()
    new_record_id = eq.last_inserted.id

    for j in range(2):
        grp_rand = randint(1, 5)
        eq_grp_id = grp_records[grp_rand].id
        eq.associate_parent(parent_id=eq_grp_id, child_id=new_record_id)

# Ensure that each group has at least 3 equation records

for i in range(grp_count):
    grp_id = grp_records['id'][i]
    eq_count_in_group = eq.record_count_for_parent(parent_id=(grp_id,))

    # Minimum number of equations in group is 3. The following doesn't loop if eq_count_in_group > 3)
    MAX_EQ_PER_GROUP = 3
    unused = eq.id_for_records_not_in_parent(parent_id=grp_id)
    n_unused = len(unused['ids'])

    n_more_in_group = MAX_EQ_PER_GROUP - eq_count_in_group
    if n_more_in_group > 0:
        eqns_to_insert = sample(range(1, n_unused), n_more_in_group)
        print(eqns_to_insert)

        for ind in eqns_to_insert:
            child_id = unused['ids'][ind]
            eq.associate_parent(parent_id=grp_id, child_id=child_id)

eq_records = eq.records
eq_count = len(eq_records)

n = 26 - var_count
for i in range(n):
    v.insert()
    new_record_id = v.last_inserted.id

for i in range(eq_count):
    eq_id = eq_records['id'][i]
    v_count_in_group = v.record_count_for_parent(parent_id=(eq_id,))

    # Minimum number of equations in group is 3. The following doesn't loop if eq_count_in_group > 3)
    MAX_VAR_PER_GROUP = 5
    unused = v.id_for_records_not_in_parent(parent_id=eq_id)
    n_unused = len(unused['ids'])

    n_more_in_group = MAX_VAR_PER_GROUP - v_count_in_group
    if n_more_in_group > 0:
        var_to_insert = sample(range(1, n_unused), n_more_in_group)
        print(var_to_insert)

        for ind in var_to_insert:
            child_id = unused['ids'][ind]
            v.associate_parent(parent_id=eq_id, child_id=child_id)
