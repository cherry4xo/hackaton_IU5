
from datetime import date
import enum
from typing import Optional
from datetime import datetime

from pydantic import UUID4
from tortoise import fields
from tortoise.models import Model
from tortoise.exceptions import DoesNotExist

from app.enums import UserRole

class CalculationTaskStatus(str, enum.Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class BaseModel(Model):
    async def to_dict(self):
        d = {}
        for field in self._meta.db_fields:
            d[field] = getattr(self, field)
        for field in self._meta.backward_fk_fields:
            d[field] = await getattr(self, field).all().values()
        return d
    
    class Meta:
        abstract = True


class TimestampMixin:
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


class User(TimestampMixin, BaseModel):
    uuid = fields.UUIDField(pk=True)
    username = fields.CharField(max_length=255, unique=True, null=True)
    email = fields.CharField(max_length=255, unique=True, null=True)
    password_hash = fields.CharField(max_length=255, null=True)
    registration_date = fields.DateField(auto_now_add=True)
    role = fields.CharEnumField(UserRole, default=UserRole.RESEARCHER, description="User role")

    def __str__(self):
        return f"{self.username} ({self.role.value})"

    class Meta:
        table = "users"

class Observatories(BaseModel):
    uuid = fields.UUIDField(pk=True)
    code = fields.CharField(max_length=16, null=False, unique=True)
    name = fields.CharField(max_length=128)
    latitude = fields.FloatField(null=False)
    longitude = fields.FloatField(null=False)
    elevation_m = fields.FloatField(null=False)

    class Meta:
        table = "Observatories"

class Comets(TimestampMixin, BaseModel):
    uuid = fields.UUIDField(pk = True)
    designation = fields.CharField(null=False, unique=True, max_length=50)
    name = fields.CharField(max_length=255)
    discovered_by: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField("models.User", related_name="discovers", on_delete=fields.CASCADE, null=False)
    discovery_date = fields.DatetimeField(null=False) 

    class Meta:
        table = "Comets"

class Observations(TimestampMixin, BaseModel):
    uuid = fields.UUIDField(pk=True)
    comet_id: fields.ForeignKeyRelation["Comets"] = fields.ForeignKeyField("models.Comets", related_name="comets", on_delete=fields.CASCADE, null=False)
    observatory_id: fields.ForeignKeyRelation["Observatories"] = fields.ForeignKeyField("models.Observatories", related_name="observatories", on_delete=fields.CASCADE, null=False)
    observer_id: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField("models.User", related_name="obsevres", on_delete = fields.CASCADE, null=False)
    observation_time = fields.DatetimeField(null=False)
    # Параметры 
    ra_deg = fields.FloatField(null=False)
    dec_deg = fields.FloatField(null=False)
    altitude_deg = fields.FloatField(null=False)
    azimuth_deg = fields.FloatField(null=False)
    processed = fields.BooleanField(default=False)

    class Meta:
        table = "Observations"

class Orbits(TimestampMixin, BaseModel):
    uuid = fields.UUIDField(pk=True)
    comet_id: fields.ForeignKeyRelation["Comets"] = fields.ForeignKeyField("models.Comets", related_name="comets", on_delete=fields.CASCADE, null=False)
    semi_major_axis = fields.FloatField()
    eccentricity = fields.FloatField()
    inclination = fields.FloatField() 
    longitude_ascending_node = fields.FloatField()
    argument_periapsis = fields.FloatField()
    periapsis_time = fields.DatetimeField()
    epoch = fields.DatetimeField()
    method = fields.CharField(default="gauss", max_length=20)
    is_hyperbolic = fields.BooleanField()

    class Meta:
        table = "Orbits"

class Close_approaches(TimestampMixin, BaseModel):
    uuid = fields.UUIDField(pk=True)
    comet_id: fields.ForeignKeyRelation["Comets"] = fields.ForeignKeyField("models.Comets", related_name="comets", on_delete=fields.CASCADE, null=False)
    approach_time = fields.DatetimeField(null=False)
    distance_au = fields.FloatField(null=True)
    distance_km = fields.FloatField(null=False)
    orbit_id: fields.ForeignKeyRelation["Orbits"] = fields.ForeignKeyField("models.Orbits", related_name="orbits", on_delete=fields.CASCADE, null=False)

    class Meta:
        table = "Close_approaches"

class CalculationTask(TimestampMixin, BaseModel):
    """
    Задача на расчёт орбиты по наблюдениям.
    Может создавать или обновлять Orbits и Close_approaches.
    """
    uuid = fields.UUIDField(pk=True)
    user: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(
        "models.User",
        related_name="calculation_tasks",
        on_delete=fields.CASCADE
    )
    comet: fields.ForeignKeyRelation["Comets"] = fields.ForeignKeyField(
        "models.Comets",
        related_name="calculation_tasks",
        null=True  # может быть null, если комета ещё неизвестна
    )
    status = fields.CharEnumField(
        CalculationTaskStatus,
        default=CalculationTaskStatus.PROCESSING
    )
    observation_start_time = fields.DatetimeField(null=True)
    observation_end_time = fields.DatetimeField(null=True)
    location_code = fields.CharField(max_length=16, null=True)  # например, "500"
    error_message = fields.TextField(null=True)

    # Внешние ключи на результаты (если расчёт успешен)
    orbit: fields.ForeignKeyRelation["Orbits"] = fields.ForeignKeyField(
        "models.Orbits",
        related_name="calculation_tasks",
        null=True
    )
    close_approach: fields.ForeignKeyRelation["Close_approaches"] = fields.ForeignKeyField(
        "models.Close_approaches",
        related_name="calculation_tasks",
        null=True
    )

    raw_observations = fields.JSONField(null=True)  # [{"observation_time": "...", "ra": 10.0, "dec": 5.0}, ...]

    class Meta:
        table = "calculation_tasks"