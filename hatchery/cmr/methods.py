from __future__ import annotations

from typing import Iterable, Optional, Sequence, Union

from django.core.exceptions import ValidationError

from core import constants as const
from cmr.models import (
    Space,
    Machine,
    SpaceCapability,
    Reservation,
)


def _get_instance(model, obj_or_id):
    """Return a model instance given either an instance or a primary key value."""
    if obj_or_id is None:
        return None
    if isinstance(obj_or_id, model):
        return obj_or_id
    return model.objects.get(pk=obj_or_id)


