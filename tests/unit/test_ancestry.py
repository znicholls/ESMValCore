from abc import ABC, abstractmethod


from esmvalcore._ancestry import _get_local_dataset


class BaseAncestryChecker(ABC):
    @property
    @abstractmethod
    def _project(self):
        pass

    @property
    @abstractmethod
    def _expected_parent_id_keys(self):
        pass

    def test_get_parent_id_keys(self):
        assert _get_local_dataset(self._project())._parent_id_keys() == self._expected_parent_id_keys()


class TestAncestryCMIP5(BaseAncestryChecker):
    def _expected_parent_id_keys(self):
        return (
            "parent_experiment",
            "parent_experiment_id",
            "parent_ensemble_member",
        )

    def _project(self):
        return "CMIP5"
