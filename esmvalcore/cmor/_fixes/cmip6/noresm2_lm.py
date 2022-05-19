"""Fixes for NorESM2-LM model."""
import numpy as np

from ..common import ClFixHybridPressureCoord
from ..fix import Fix


class AllVars(Fix):
    """Fixes for all variables."""

    def fix_metadata(self, cubes):
        """Fix metadata.

        Longitude boundary description may be wrong (lon=[0, 2.5, ..., 355,
        357.5], lon_bnds=[[0, 1.25], ..., [356.25, 360]]).

        Parameters
        ----------
        cubes: iris.cube.CubeList
            Input cubes to fix.

        Returns
        -------
        iris.cube.CubeList

        """
        for cube in cubes:
            coord_names = [cor.standard_name for cor in cube.coords()]
            if 'longitude' in coord_names:
                if cube.coord('longitude').ndim == 1 and \
                        cube.coord('longitude').has_bounds():
                    lon_bnds = cube.coord('longitude').bounds.copy()
                    if cube.coord('longitude').points[0] == 0. and \
                            lon_bnds[0][0] == 0.:
                        lon_bnds[0][0] = -1.25
                    if cube.coord('longitude').points[-1] == 357.5 and \
                            lon_bnds[-1][-1] == 360.:
                        lon_bnds[-1][-1] = 358.75
                    cube.coord('longitude').bounds = lon_bnds

            if cube.attributes.get('experiment_id', '').startswith("esm-ssp585"):
                parent_time_units = "parent_time_units"
                parent_time_units_bad_value = "days since 0421-01-01"

                branch_time_in_parent = "branch_time_in_parent"
                branch_time_in_parent_bad_value = 60225.0
                try:
                    bad_parent_time_units = cube.attributes[parent_time_units] == parent_time_units_bad_value
                    bad_branch_time_in_parent = cube.attributes[branch_time_in_parent] == branch_time_in_parent_bad_value
                    if bad_parent_time_units and bad_branch_time_in_parent:
                        cube.attributes[parent_time_units] = "days since 0001-01-01"
                        cube.attributes[branch_time_in_parent] = 735110.0
                except AttributeError:
                    pass

        return cubes


Cl = ClFixHybridPressureCoord


Cli = ClFixHybridPressureCoord


Clw = ClFixHybridPressureCoord


class Siconc(Fix):
    """Fixes for siconc."""

    def fix_metadata(self, cubes):
        """Fix metadata.

        Some coordinate points vary for different files of this dataset (for
        different time range). This fix removes these inaccuracies by rounding
        the coordinates.

        Parameters
        ----------
        cubes: iris.cube.CubeList
            Input cubes to fix.

        Returns
        -------
        iris.cube.CubeList

        """
        for cube in cubes:
            latitude = cube.coord('latitude')
            latitude.bounds = np.round(latitude.bounds, 4)
            longitude = cube.coord('longitude')
            longitude.bounds = np.round(longitude.bounds, 4)

        return cubes
