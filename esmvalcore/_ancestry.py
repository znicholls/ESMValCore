"""Module for navigating a file's ancestry in the ESMValTool."""
from abc import ABC, abstractmethod


class LocalDataset(ABC):
    @property
    @abstractmethod
    def _project(self):
        pass

    @property
    @abstractmethod
    def _parent_id_keys(self):
        pass


class LocalDatasetCMIP5(LocalDataset):
    def _project(self):
        "CMIP5"

    def _parent_id_keys(self):
        return (
            "parent_experiment",
            "parent_experiment_id",
            "parent_ensemble_member",
        )


def _get_local_dataset(project):
    """
    Get an instance of :class:`LocalDatasetC` for a given project
    """
    if project == "CMIP5":
        return LocalDatasetCMIP5()

    raise NotImplementedError(f"No LocalDataset for {project}")
