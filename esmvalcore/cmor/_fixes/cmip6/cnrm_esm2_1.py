"""Fixes for CNRM-ESM2-1 model."""
from ..fix import Fix
from .cnrm_cm6_1 import Cl as BaseCl
from .cnrm_cm6_1 import Clcalipso as BaseClcalipso
from .cnrm_cm6_1 import Cli as BaseCli
from .cnrm_cm6_1 import Clw as BaseClw
from .cnrm_cm6_1 import Omon as BaseOmon


class AllVars(Fix):
    """Fixes for all vars."""

    def fix_metadata(self, cubes):
        """Fix metadata

        Parameters
        ----------
        cubes : iris.cube.CubeList
            Input cubes.

        Returns
        -------
        iris.cube.CubeList

        """
        for cube in cubes:
            if cube.attributes.get('experiment_id', '') == 'G6solar':
                branch_time_in_parent = "branch_time_in_parent"
                bad_value = 0.0
                for cube in cubes:
                    try:
                        if cube.attributes[branch_time_in_parent] == bad_value:
                            cube.attributes[branch_time_in_parent] = 60265.
                    except AttributeError:
                        pass
        return cubes


Cl = BaseCl


Clcalipso = BaseClcalipso


Cli = BaseCli


Clw = BaseClw


Omon = BaseOmon
