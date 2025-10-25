
from datetime import date
import enum
from typing import Optional
from datetime import datetime

from pydantic import UUID4
from tortoise import fields
from tortoise.models import Model
from tortoise.exceptions import DoesNotExist

from app.utils import password
from app.schemas import UserCreate, CreateEquipment, CreateAuditorium, CreateAvailability, CreateBooking
from app.enums import UserRole


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
    role = fields.CharEnumField(UserRole, default=UserRole.BOOKER, description="User role")

    @classmethod
    async def create(cls, user: UserCreate) -> "User":
        user_dict = user.model_dump(exclude=["password"])
        password_hash = password.get_password_hash(password=user.password)
        model = cls(**user_dict, password_hash=password_hash, registration_date=date.today())
        return model
    
    @classmethod
    async def get_by_uuid(cls, uuid: UUID4) -> "User":
        try:
            query = cls.get_or_none(uuid=uuid)
            user = await query
            return user
        except DoesNotExist:
            return None

    @classmethod
    async def get_by_username(cls, username: str) -> Optional["User"]:
        try:
            query = cls.get_or_none(username=username)
            user = await query
            return user
        except DoesNotExist:
            return None
        
    @classmethod 
    async def get_by_email(cls, email: str) -> Optional["User"]:
        try:
            query = cls.get_or_none(email=email)
            user = await query
            return user
        except DoesNotExist:
            return None

    def __str__(self):
        return f"{self.username} ({self.role.value})"

    class Meta:
        table = "users"

class Observatories(BaseModel):
    uuid = fields.UUIDField(pk=True)
    code = fields.CharField(max_length=16, null=False, unique=True)
    name = fields.CharEnumField(max_length=128)
    latitude = fields.FloatField(null=False)
    longitude = fields.FloatField(null=False)
    elevation_m = fields.FloatField(null=False)

    class Meta:
        table = "Observatories"

class Comets(TimestampMixin, BaseModel):
    uuid =  fields.UUIDField(pk = True)
    designation = fields.CharField(null=False, unique=True, max_length=50) #????????????????????????????????
    name = fields.CharField()
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
    epoch TIMESTAMP = fields.DatetimeField()
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