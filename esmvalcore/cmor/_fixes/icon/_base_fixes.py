"""Fix base classes for ICON on-the-fly CMORizer."""

import logging
import warnings
from datetime import datetime
from pathlib import Path
from shutil import copyfileobj
from urllib.parse import urlparse

import iris
import requests
from iris import NameConstraint

from ..fix import Fix

logger = logging.getLogger(__name__)


class IconFix(Fix):
    """Base class for all ICON fixes."""

    CACHE_DIR = Path.home() / '.esmvaltool' / 'cache'
    CACHE_VALIDITY = 7 * 24 * 60 * 60  # [s]; = 1 week
    TIMEOUT = 5 * 60  # [s]; = 5 min
    GRID_FILE_ATTR = 'grid_file_uri'

    def __init__(self, *args, **kwargs):
        """Initialize ICON fix."""
        super().__init__(*args, **kwargs)
        self._horizontal_grids = {}

    def add_coord_from_grid_file(self, cube, coord_name,
                                 target_coord_long_name):
        """Add coordinate from grid file to cube.

        Note
        ----
        Assumes that the input cube has a single unnamed dimension, which will
        be used as dimension for the new coordinate.

        Parameters
        ----------
        cube: iris.cube.Cube
            ICON data to which the coordinate from the grid file is added.
        coord_name: str
            Name of the coordinate in the grid file. Must be one of
            ``'grid_latitude'``, ``'grid_longitude'``.
        target_coord_long_name: str
            Long name that is assigned to the newly added coordinate.

        Raises
        ------
        ValueError
            Invalid ``coord_name`` is given; input cube does not contain a
            single unnamed dimension that can be used to add the new
            coordinate.

        """
        allowed_coord_names = ('grid_latitude', 'grid_longitude')
        if coord_name not in allowed_coord_names:
            raise ValueError(
                f"coord_name must be one of {allowed_coord_names}, got "
                f"'{coord_name}'")
        horizontal_grid = self.get_horizontal_grid(cube)

        # Use 'cell_area' as dummy cube to extract coordinates
        # Note: it might be necessary to expand this when more coord_names are
        # supported
        grid_cube = horizontal_grid.extract_cube(
            NameConstraint(var_name='cell_area'))
        coord = grid_cube.coord(coord_name)

        # Find index of horizontal coordinate (= single unnamed dimension)
        n_unnamed_dimensions = cube.ndim - len(cube.dim_coords)
        if n_unnamed_dimensions != 1:
            raise ValueError(
                f"Cannot determine coordinate dimension for coordinate "
                f"'{target_coord_long_name}', cube does not contain a single "
                f"unnamed dimension:\n{cube}")
        coord_dims = ()
        for idx in range(cube.ndim):
            if not cube.coords(dimensions=idx, dim_coords=True):
                coord_dims = (idx,)
                break

        coord.standard_name = None
        coord.long_name = target_coord_long_name
        cube.add_aux_coord(coord, coord_dims)

    def get_cube(self, cubes, var_name=None):
        """Extract single cube.

        Parameters
        ----------
        cubes: iris.cube.CubeList
            Input cubes.
        var_name: str, optional
            If given, use this var_name to extract the desired cube. If not
            given, use the raw_name given in extra_facets (if possible) or the
            short_name of the variable to extract the desired cube.

        Returns
        -------
        iris.cube.Cube
            Desired cube.

        Raises
        ------
        ValueError
            Desired variable is not available in the input cubes.

        """
        if var_name is None:
            var_name = self.extra_facets.get('raw_name',
                                             self.vardef.short_name)
        if not cubes.extract(NameConstraint(var_name=var_name)):
            raise ValueError(
                f"Variable '{var_name}' used to extract "
                f"'{self.vardef.short_name}' is not available in input file")
        return cubes.extract_cube(NameConstraint(var_name=var_name))

    def get_horizontal_grid(self, cube):
        """Get ICON horizontal grid from global attribute of cube.

        Note
        ----
        If necessary, this functions downloads the grid file to a cache
        directory. The downloaded file is valid for 7 days until it is
        downloaded again.

        Parameters
        ----------
        cube: iris.cube.Cube
            Cube for which the ICON horizontal grid is retrieved. This cube
            needs the global attribute given by ``self.GRID_FILE_ATTR``.

        Returns
        -------
        iris.cube.CubeList
            ICON horizontal grid.

        Raises
        ------
        ValueError
            Input cube does not contain the necessary attribute to download the
            ICON horizontal grid file (see ``self.GRID_FILE_ATTR``)

        """
        if self.GRID_FILE_ATTR not in cube.attributes:
            raise ValueError(
                f"Cube does not contain the attribute '{self.GRID_FILE_ATTR}' "
                f"necessary to download the ICON horizontal grid file:\n"
                f"{cube}")
        grid_url = cube.attributes[self.GRID_FILE_ATTR]

        # If already loaded, return the horizontal grid (cube)
        parsed_url = urlparse(grid_url)
        grid_name = Path(parsed_url.path).name
        if grid_name in self._horizontal_grids:
            return self._horizontal_grids[grid_name]

        # Check if grid file has recently been downloaded and load it if
        # possible
        grid_path = self.CACHE_DIR / grid_name
        if grid_path.exists():
            mtime = grid_path.stat().st_mtime
            now = datetime.now().timestamp()
            age = now - mtime
            if age < self.CACHE_VALIDITY:
                logger.debug("Using cached ICON grid file '%s'", grid_path)
                self._horizontal_grids[grid_name] = self._load_cubes(grid_path)
                return self._horizontal_grids[grid_name]
            logger.debug("Existing cached ICON grid file '%s' is outdated",
                         grid_path)

        # Download file if necessary
        logger.debug("Attempting to download ICON grid file from '%s' to '%s'",
                     grid_url, grid_path)
        with requests.get(grid_url, stream=True,
                          timeout=self.TIMEOUT) as response:
            response.raise_for_status()
            with open(grid_path, 'wb') as file:
                copyfileobj(response.raw, file)
        logger.info("Successfully downloaded ICON grid file from '%s' to '%s'",
                    grid_url, grid_path)

        self._horizontal_grids[grid_name] = self._load_cubes(grid_path)
        return self._horizontal_grids[grid_name]

    @staticmethod
    def _load_cubes(path):
        """Load cubes and ignore certain warnings."""
        with warnings.catch_warnings():
            warnings.filterwarnings(
                'ignore',
                message="Ignoring netCDF variable .* invalid units .*",
                category=UserWarning,
                module='iris',
            )
            cubes = iris.load(str(path))
        return cubes
