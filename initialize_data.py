from equation_group import EquationGroup
from equation import Equation
from variable import Variable

eq_grp = EquationGroup()
eq = Equation()
v = Variable()

for cnt in range(1, 6):
    eq_grp.insert()

    eq.insert(parent_id=eq_grp.last_inserted.id)
    v.insert(parent_id=eq.last_inserted.id)

