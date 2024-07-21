from django.conf import settings
import logging
import functools
from time import sleep
logger = logging.getLogger(__name__)

def wait_for_movement_completion(func):
    @functools.wraps(func)
    def wrapper_wait_for_movement_completion(self, *args, **kwargs):
        response=func(self, *args, **kwargs)
        
        # Poll the status of the camera's movement
        while True:
            
            status = self.camera_ptz.GetStatus({'ProfileToken': self.camera_media_profile.token})
            
            # Assuming 'Moving' is a boolean attribute indicating movement status
            if status.MoveStatus.PanTilt=='IDLE' and status.MoveStatus.Zoom=='IDLE':
                logger.info("Movement completed.")
                break

            # Sleep for a short period before checking the status again
            sleep(0.5)
        return response
    return wrapper_wait_for_movement_completion