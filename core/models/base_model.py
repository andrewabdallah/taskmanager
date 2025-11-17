import uuid as uuid_util

from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone

from core.constants import ROWS_BATCH_SIZE


class CustomQueryset(QuerySet):
    """Custom queryset for the BaseSyncModel model."""

    def delete(self, *args, permanent: bool = False, **kwargs):
        """Ensure that delete is a soft delete even for bulk actions."""
        if permanent is True:
            return super().delete(*args, **kwargs)
        return self.update(deleted=True)

    def recover(self):
        """Bulk recovery of soft deleted objects."""
        return self.update(deleted=False)

    def bulk_update(self, *args, **kwargs):
        """
        This function is used to make sure that all elements have updated their time stamp.
        so the caller don't care about the updated time stamp and here the function take care of it
        then it updates them in batches
        """
        objs = kwargs["objs"] if "objs" in kwargs else args[0]
        fields = kwargs["fields"] if "fields" in kwargs else args[1]
        for element in objs:
            element.updated_at = timezone.now()
        if "updated_at" not in fields:
            fields.append("updated_at")
        return super().bulk_update(objs=objs, fields=fields, batch_size=ROWS_BATCH_SIZE)

    def active(self):
        return self.filter(deleted=False)

    def bulk_update_without_timestamp(self, *args, **kwargs):
        """
        This function is just used to update the data in batches,
        and it doesn't check for updated time stamp
        so the caller should be responsible for updating elements with an updated time stamp
        """
        objs = kwargs["objs"] if "objs" in kwargs else args[0]
        fields = kwargs["fields"] if "fields" in kwargs else args[1]
        return super().bulk_update(objs=objs, fields=fields, batch_size=ROWS_BATCH_SIZE)


class BaseModel(models.Model):
    """Abstract base model with common fields and soft delete functionality."""

    id = models.UUIDField(primary_key=True, default=uuid_util.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    # Fields we always want to update on save for all models
    BASE_UPDATE_FIELDS = ["updated_at"]
    # Auto update fields and fields updated in signals for a specific model
    DEFAULT_UPDATE_FIELDS = None

    # Use the custom queryset to retrieve all objects including soft deleted ones
    objects = CustomQueryset.as_manager()

    # Fields to check for updates on save
    FIELDS_TO_WATCH_FOR_CHANGES = []

    class Meta:
        abstract = True
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["updated_at"], name="base_updated_at_idx"),
        ]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # Set old values of fields to watch for changes
        self.set_old_values()
        self._update_fields = self._default_update_fields

    def __setattr__(self, name: str, value, /) -> None:
        if hasattr(self, "_update_fields") and (
            not name.startswith("_")
            and name not in ["id", "pk"]
            and name in {f.name for f in self._meta.get_fields() if f.editable}
            and hasattr(self, name)
        ):
            self._update_fields.append(name)
        return super().__setattr__(name, value)

    def save(self, *args, **kwargs):
        # we don't need to pass _update_fields on instance creation and
        # when we explicitly set update_fields when saving
        if self._state.adding or "update_fields" in kwargs:
            super().save(*args, **kwargs)
        else:
            super().save(update_fields=self._update_fields)
        self.set_old_values()
        self._update_fields = self._default_update_fields

    def set_old_values(self):
        # Reset old values of fields to watch for changes
        for field in self.FIELDS_TO_WATCH_FOR_CHANGES:
            setattr(self, f"old_{field}", getattr(self, field, None))

    def get_old_value(self, field_name: str):
        """
        Get the old value of a field
        :raises: RuntimeError if the field is not being watched for changes
        """
        try:
            return getattr(self, f"old_{field_name}")
        except AttributeError as e:
            raise RuntimeError(
                f"Field {field_name} is not being watched for changes"
            ) from e

    def has_changed(self, field_name: str) -> bool:
        """
        Check if a field has changed since the last save
        :raises: RuntimeError if the field is not being watched for changes
        """
        try:
            return getattr(self, f"old_{field_name}") != getattr(self, field_name)
        except AttributeError as e:
            raise RuntimeError(
                f"Field {field_name} is not being watched for changes"
            ) from e

    def delete(self, *args, permanent: bool = False, **kwargs):
        """Soft delete the object unless permanent is True."""
        if permanent is True:
            return super().delete(*args, **kwargs)
        self.deleted = True
        self.save(update_fields=["deleted"])
        return self

    def recover(self):
        """Recover a soft deleted object."""
        self.deleted = False
        self.save()

    # Use the custom queryset to retrieve only non-deleted objects
    @property
    def active_objects(self):
        return self.objects.active()

    @property
    def _default_update_fields(self):
        return self.BASE_UPDATE_FIELDS + (self.DEFAULT_UPDATE_FIELDS or [])
