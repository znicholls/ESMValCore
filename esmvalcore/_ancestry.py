"""Module for navigating a file's ancestry in the ESMValTool."""
from abc import ABCMeta, abstractmethod
from pathlib import Path

import iris

from ._data_finder import _find_input_files


class NoLocalParentError(ValueError):
    """Exception raised when the parent for a dataset cannot be found
    locally."""


class NoESGFParentError(ValueError):
    """Exception raised when the parent for a dataset cannot be found on
    ESGF."""


class ParentFinder(metaclass=ABCMeta):
    def __init__(self, cube):
        """
        Class for finding the parents (in the CMIP sense i.e. the experiment
        from which a given experiment branched) of datasets

        Parameters
        ----------
        cube : :obj:`pathlib.Path`
            Cube containing metadata used for searching etc.
        """
        if not isinstance(cube, iris.cube.Cube):
            raise TypeError("`cube` must be an :obj:`iris.cube.Cube`")

        self._cube = cube

    @property
    @abstractmethod
    def _project(self):
        """str: Name of the project to which this dataset belongs"""

    @property
    @abstractmethod
    def _esmval_map_metadata_keys_parent_info(self):
        """Dict[str: str] Map from keys in metadata which provide information about the parent to ESMValTool names.

        Keys should appear exactly as they are in the attributes of the
        datasets, values should follow the ESMValCore internal naming
        conventions.
        """

    @property
    @abstractmethod
    def _esmval_map_metadata_keys_file_info(self):
        """Tuple[str] Maximum set of metadata required to uniquely identify a dataset.

        Names should appear exactly as they are in the attributes of the
        datasets i.e. do not translate to ESMValCore internal naming
        conventions.
        """

    def get_parent_metadata(self):
        """Get the parent file's metadata
        """
        parent_metadata = {
            **self._get_esmval_data_ids(),
            **self._get_esmval_parent_ids(),
        }

        return parent_metadata

    def _get_esmval_data_ids(self):
        out = {
            esmval_name: self._cube.attributes[k]
            for k, esmval_name
            in self._esmval_map_metadata_keys_file_info.items()
        }

        return out

    def _get_esmval_parent_ids(self):
        out = {
            esmval_name: self._cube.attributes[k]
            for k, esmval_name
            in self._esmval_map_metadata_keys_parent_info.items()
        }

        return out

    def find_local_parent(self, rootpath, drs):
        """Find parent files locally.

        Parameters
        ----------
        rootpath : :obj:`pathlib.Path`
            Root path of local files

        drs : str
            Data reference syntax used for local files

        Returns
        -------
        list[:obj:`pathlib.Path`]
            Path to files in the parent dataset

        Raises
        ------
        NoLocalParentError
            No parent files could be found locally
        """
        parent_metadata = self.get_parent_metadata()
        parents = self._find_parent_files(parent_metadata, rootpath, drs)

        if not parents:
            error_msg = "something helpful"
            raise NoLocalParentError(error_msg)

        return [Path(p) for p in parents]

    def _find_parent_files(self, parent_metadata, rootpath, drs):
        metadata_in = {
            # not sure why this original_short_name is needed for file
            # searching but ok
            "original_short_name": parent_metadata["short_name"],
            **parent_metadata,
        }
        (res, _, _) = _find_input_files(
            variable=metadata_in,
            rootpath={self._project: [rootpath]},
            drs={self._project: drs},
        )

        return res

    def find_esgf_parent(self):
        """Find parent files on ESGF.

        Returns
        -------
        list[:obj:`ESGFFile`]
            ESGF files in the parent dataset

        Raises
        ------
        NoESGFParentError
            No parent files could be found on ESGF

        Notes
        -----
        Sub-classes of :obj:`ParentFinder` which relate to datasets that cannot be
        downloaded from ESGF should simply implement this method with
        ``raise NotImplementedError``.
        """


class ParentFinderCMIP5(ParentFinder):
    _project = "CMIP5"
    _esmval_map_metadata_keys_parent_info = {
        "parent_experiment": "exp",
        "parent_experiment_rip": "ensemble",
    }
    _esmval_map_metadata_keys_file_info = {
        "experiment": "exp",
        "institute_id": "institute",
        "model_id": "dataset",
        "project_id": "project",
    }

    def _get_esmval_data_ids(self):
        ids = super()._get_esmval_data_ids()
        # variable name not in data
        ids["short_name"] = self._cube.var_name
        attrs = self._cube.attributes
        ids["ensemble"] = f"r{attrs['realization']}i{attrs['initialization_method']}p{attrs['physics_version']}"
        # info not in data attributes so let it guess
        ids["activity"] = "*"
        ids["mip"] = "*"
        ids["grid"] = "*"

        return ids


class ParentFinderCMIP6(ParentFinder):
    _project = "CMIP6"
    _esmval_map_metadata_keys_parent_info = {
        "parent_activity_id": "activity",
        "parent_experiment_id": "exp",
        "parent_mip_era": "project",
        "parent_source_id": "dataset",
        "parent_variant_label": "ensemble",
    }
    _esmval_map_metadata_keys_file_info = {
        "activity_id": "activity",
        "experiment_id": "exp",
        "grid_label": "grid",
        "institution_id": "institute",
        "mip_era": "project",
        "source_id": "dataset",
        "table_id": "mip",
        "variable_id": "short_name",
        "variant_label": "ensemble",
    }


def get_parent_finder(project):
    """Get an instance of :class:`ParentFinder` for a given project.

    Parameters
    ----------
    project : str
        Project

    Returns
    -------
    :obj:`ParentFinder`

    Raises
    ------
    NotImplementedError
        There is no implementation of :obj:`ParentFinder` for the requested
        project
    """
    if project == "CMIP5":
        return ParentFinderCMIP5()

    if project == "CMIP6":
        return ParentFinderCMIP6()

    raise NotImplementedError(f"No ParentFinder for {project}")
