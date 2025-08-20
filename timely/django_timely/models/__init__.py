import logging

from .assets import Asset, AssetType, AssetGroup, Venue
# from .bookings import BookingRequest, EventParticipant, EventParticipantAsset
from .bookings import EventParticipant, EventParticipantAsset
from .events import Event, EventType

logger = logging.getLogger(__name__)

# Try to auto register the models with `django-auditlog`
try:
    from config.settings import INSTALLED_APPS

    logger.info("Found `django-auditlog` in installed apps.")

    if "auditlog" in INSTALLED_APPS:
        from auditlog.registry import auditlog  # pyright: ignore[reportMissingImports]

        models_to_audit_log = [
            Event,
            EventType,
            Asset,
            AssetType,
            AssetGroup,
            Venue,
            # BookingRequest,
            EventParticipant,
            EventParticipantAsset,
        ]
        for _model in models_to_audit_log:
            _model_name = _model.__class__.__name__
            logger.info(f"Registering {_model_name} with `django-auditlog")
            auditlog.register(_model)
            logger.info(f"{_model_name} successfully registered with `django-auditlog`")

except ImportError:
    pass
