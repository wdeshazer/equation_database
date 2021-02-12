"""
This is an example that was being used at first, but has since been abondoned
"""
import warnings
from warnings import warn
from typing import Optional
from pandas import DataFrame


class NoRecordIDError(UserWarning):
    """UserWarning for EquationGroup"""


class NoGroupRecordAssociationsError(UserWarning):
    """UserWarning for EquationGroup"""


def selected_data_df(self, parent_id: int = None) -> DataFrame:
    """Retern selected data in DataFrame form"""

    df: Optional[DataFrame] = None

    try:
        df = self.grouped_data.loc[parent_id, :]
    except KeyError:
        inds = self.grouped_data.index
        parent_ind_values = inds.get_level_values(self.parent_table_id_name())

        def warning_no_group_records(message, category, filename, lineno):  # file=None, line=None):
            return ' File "%s", line %s, \n\t%s: %s\n' % (filename, lineno, category.__name__, message)

        warnings.formatwarning = warning_no_group_records

        if parent_ind_values.isna().all():
            txt = "There are no records in {parent}".format(parent=self.parent_table_name)
            warn(txt, NoGroupRecordAssociationsError)
        else:
            txt = "There is no record in {parent} with id= {id}".format(
                parent=self.parent_table_name, id=parent_id)
            warn(txt, NoRecordIDError)

    return df
