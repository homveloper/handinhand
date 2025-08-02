from dataclasses import dataclass
from datetime import datetime
from typing import Any, TypeVar, Type, cast
import dateutil.parser


T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_datetime(x: Any) -> datetime:
    return dateutil.parser.parse(x)


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


@dataclass
class ProfileEntitySchema:
    """User profile information entity"""

    avatar: str
    """Avatar identifier"""

    created_at: datetime
    """Account creation timestamp"""

    exp: int
    """Experience points"""

    level: int
    """User level"""

    nickname: str
    """User nickname"""

    @staticmethod
    def from_dict(obj: Any) -> 'ProfileEntitySchema':
        assert isinstance(obj, dict)
        avatar = from_str(obj.get("avatar"))
        created_at = from_datetime(obj.get("created_at"))
        exp = from_int(obj.get("exp"))
        level = from_int(obj.get("level"))
        nickname = from_str(obj.get("nickname"))
        return ProfileEntitySchema(avatar, created_at, exp, level, nickname)

    def to_dict(self) -> dict:
        result: dict = {}
        result["avatar"] = from_str(self.avatar)
        result["created_at"] = self.created_at.isoformat()
        result["exp"] = from_int(self.exp)
        result["level"] = from_int(self.level)
        result["nickname"] = from_str(self.nickname)
        return result


def profile_entity_schema_from_dict(s: Any) -> ProfileEntitySchema:
    return ProfileEntitySchema.from_dict(s)


def profile_entity_schema_to_dict(x: ProfileEntitySchema) -> Any:
    return to_class(ProfileEntitySchema, x)
