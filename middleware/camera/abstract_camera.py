from abc import ABC, abstractmethod

from middleware.camera.types import CameraAsset


class AbstractCameraController(ABC):
    @abstractmethod
    def go_to_preset(self, preset_id: str):
        pass

    @abstractmethod
    def get_presets(self, req: CameraAsset):
        pass

    @abstractmethod
    def get_status(self, req: CameraAsset):
        pass

    @abstractmethod
    def absolute_move(self, pan: float, tilt: float, zoom: float):
        pass

    @abstractmethod
    def relative_move(self, pan: float, tilt: float, zoom: float):
        pass

    @abstractmethod
    def set_preset(self, preset_name: str):
        pass

    @abstractmethod
    def get_snapshot_uri(self):
        pass
