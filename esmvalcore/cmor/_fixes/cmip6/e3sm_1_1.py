"""Fixes for E3SM-1-1 model."""
from ..fix import Fix

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
            if cube.attributes.get('experiment_id', '').startswith("ssp"):
                branch_time_in_parent = "branch_time_in_parent"
                bad_value = 0.0
                for cube in cubes:
                    try:
                        if cube.attributes[branch_time_in_parent] == bad_value:
                            cube.attributes[branch_time_in_parent] = 60265.
                    except AttributeError:
                        pass

        return cubes
