"""Module for navigating a file's ancestry in the ESMValTool."""
from abc import ABCMeta, abstractmethod


class LocalDataset(metaclass=ABCMeta):
    @property
    @abstractmethod
    def _project(self):
        """str: Name of the project to which this dataset belongs"""

    @property
    @abstractmethod
    def _parent_id_keys(self):
        """List[str] Attributes which can be used to identify the parent of a dataset"""

    def get_parent_ids(self, attrs):
        """
        Get parent ids

        Parameters
        ----------
        attrs : Dict[str: str]
            Attributes from which to get parent ids

        Returns
        -------
        Dict[str: str]
            Parent ids, using the keys as they are in the attributes
        """
        return {
            k: attrs[k].replace(" ", "")
            for k in self._parent_id_keys
        }

    # Next: get_parent_search_ids
    # Two steps:
    #   - get_parent_ids_esmvaltool_keys and then join with self's
    #   - attributes

    # Then: find_parent_files
    # Use `variable`, replace attributes with results from
    # get_parent_search_ids then use find_files
    # Not sure how to then use automated downloads


class LocalDatasetCMIP5(LocalDataset):
    _project = "CMIP5"
    _parent_id_keys = (
        "parent_experiment_id",
        "parent_experiment_rip",
    )


class LocalDatasetCMIP6(LocalDataset):
    _project = "CMIP6"
    _parent_id_keys = (
        "parent_activity_id",
        "parent_experiment_id",
        "parent_mip_era",
        "parent_source_id",
        "parent_variant_label",
    )


def _get_local_dataset(project):
    """
    Get an instance of :class:`LocalDatasetC` for a given project
    """
    if project == "CMIP5":
        return LocalDatasetCMIP5()

    if project == "CMIP6":
        return LocalDatasetCMIP6()

    raise NotImplementedError(f"No LocalDataset for {project}")
