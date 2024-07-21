from abc import ABC,abstractmethod

from middleware.camera.types import CameraAsset





class AbstractCameraController(ABC):
    
    @abstractmethod
    def go_to_preset(self,preset_name: str):
        pass

    @abstractmethod
    def get_presets(req:CameraAsset):
        pass

    @abstractmethod  
    def get_status(req:CameraAsset):
        pass
