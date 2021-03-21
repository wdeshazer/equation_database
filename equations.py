"""
Equation Provides helper functions for managing Equation and their associations
"""

__author__ = "William DeShazer"
__version__ = "0.1.0"
__license__ = "MIT"

from collections import namedtuple
from typing import Optional, List
from grouped_physics_object import GroupedPhysicsObject, add_field
from physics_objects import PhysicsObject, PhysicsObjects
from latex_data import LatexData
from time_logging import TimeLogger

GroupedEquationRecord = namedtuple(
    'GroupedEquationRecord', ['code_file_path', 'insertion_order', 'insertion_order_prev',
                              'insertion_date', 'inserted_by', 'name', 'latex', 'notes', 'image',
                              'template_id', 'image_is_dirty', 'created_at', 'created_by',
                              'modified_at', 'modified_by', 'compiled_at', 'dimensions', 'unit_id',
                              'type_name', 'associated_code_file', 'latex_obj'])

GroupedEquationRecords = List[GroupedEquationRecord]


class EquationRecord(PhysicsObject):
    """Creates a unique Signature for an Equation Record"""


EquationRecords = List[EquationRecord]

NewEquationRecordInput = \
    namedtuple('EquationRecordInput',
               ['name', 'latex_obj', 'notes', 'created_by', 'dimensions', 'unit_id', 'type_name'])

ExistingEquationRecordInput = \
    namedtuple('ExistingEquationRecordInput',
               ['equation_id', 'name', 'latex_obj', 'modified_by', 'dimensions', 'unit_id', 'type_name'])


class GroupedEquations(GroupedPhysicsObject):
    """Equation class provides helper functions for inserting equations into the database"""

    def __init__(self, *args, table_name='equation', parent_table_name='eqn_group', verbose: bool = False, **kwargs):
        """Constructor for Equation"""
        super().__init__(*args, table_name=table_name, parent_table_name=parent_table_name, verbose=verbose, **kwargs)

        if len(self.grouped_data.index) == 0:
            # https://en.wikipedia.org/wiki/Proof_that_22/7_exceeds_%CF%80
            ltx = LatexData(latex=r'\begin{equation*}' '\n'
                                  r'\Sigma \Nu = \int_{0}^{1} \frac{x^4 \left(1 - x \right)^4 }{1 + x^2} dx' '\n'
                                  r'\end{equation}')
            self.new_record(name='Genesis',
                            latex=ltx,
                            notes='In the beginning', dimensions=1, created_by='razor', my_conn=self.my_conn
                            )

    # pylint: disable=arguments-differ
    def new_record(self, *args, latex: Optional[LatexData] = None, type_name='Undesignated', **kwargs):
        """Insert new Equation"""
        # new_record is for passing arguments that exceed the arguments in GroupedPhysicsObject
        new_record = {'type_name': type_name}
        if latex is None:
            latex = self.grouped_data.iloc[0].latex_obj
        super().new_record(*args, new_record=new_record, latex=latex, **kwargs)

    def update(self, *args, data: Optional[dict] = None, type_name: str = None, **kwargs):
        """Update Equation"""
        if data is None:
            data = {}
        data.update(add_field('type_name', type_name))
        super().update(*args, data=data, **kwargs)

    def associate_parent(self, parent_id: int = None, child_id: int = None,
                         insertion_order: int = None, inserted_by: str = None,
                         code_file_path: str = None,  new_record: dict = None,
                         my_conn: Optional[dict] = None, t_log: Optional[TimeLogger] = None,
                         verbose: bool = False):

        # noinspection PyTypeChecker
        new_record: dict = None

        if code_file_path is not None:
            new_record = dict(code_file_path=code_file_path)

        super().associate_parent(parent_id=parent_id, child_id=child_id,
                                 insertion_order=insertion_order, inserted_by=inserted_by,
                                 my_conn=my_conn, t_log=t_log,
                                 new_record=new_record, verbose=verbose)


class Equations(PhysicsObjects):
    """Data associated with Equations exclusively, independent of how they are grouped"""

    def __init__(self, *args, table_name: str = 'equation', **kwargs):
        super().__init__(*args, table_name=table_name, **kwargs)

    def record(self, an_id: int = None):
        phy_obj = super().record(an_id)
        rcd = EquationRecord(*phy_obj)
        return rcd
