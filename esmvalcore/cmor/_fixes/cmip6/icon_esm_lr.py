"""Fixes for ICON-ESM-LR model."""

from ..fix import Fix


class AllVars(Fix):
    """Fixes for all variables."""

    def fix_metadata(self, cubes):
        """Rename ``long_name`` of latitude to latitude (may be Latitude).

        Parameters
        ----------
        cubes : iris.cube.CubeList
            Input cubes.

        Returns
        -------
        iris.cube.Cube
        """
        #coords_longnames_to_change = {
        #    'latitude': 'latitude',
        #}

        #for cube in cubes:
        #    for (std_name, long_name) in coords_longnames_to_change.items():
        #        coord = cube.coord(std_name)
        #        if coord.long_name != long_name:
        #            coord.long_name = long_name

        coords_to_change = {
            'latitude': 'lat',
            'longitude': 'lon',
        }
        for cube in cubes:
            for (std_name, var_name) in coords_to_change.items():
                try:
                    coord = cube.coord(std_name)
                except iris.exceptions.CoordinateNotFoundError:
                    pass
                else:
                    coord.var_name = var_name
        return cubes
