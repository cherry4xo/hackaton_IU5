import enum

class UserRole(str, enum.Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

    """ Defines the roles a user can have """
    RESEARCHER = "researcher"
    MODERATOR = "moderator"


class CalculationTaskType(str, enum.Enum):
    ORBIT_CALCULATION = "orbit_calculation"
    CLOSEST_APPROACH = "closest_approach"
