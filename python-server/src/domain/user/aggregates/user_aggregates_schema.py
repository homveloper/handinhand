from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, TypeVar, Callable, Type, cast
from datetime import datetime
import dateutil.parser


T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def from_dict(f: Callable[[Any], T], x: Any) -> Dict[str, T]:
    assert isinstance(x, dict)
    return { k: f(v) for (k, v) in x.items() }


def to_enum(c: Type[EnumT], x: Any) -> EnumT:
    assert isinstance(x, c)
    return x.value


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_datetime(x: Any) -> datetime:
    return dateutil.parser.parse(x)


class Rarity(Enum):
    """Item rarity (optional)"""

    COMMON = "common"
    EPIC = "epic"
    LEGENDARY = "legendary"
    RARE = "rare"
    UNCOMMON = "uncommon"


@dataclass
class Item:
    id: str
    """Item identifier"""

    quantity: int
    """Item quantity"""

    level: Optional[int] = None
    """Item level (optional)"""

    properties: Optional[Dict[str, Any]] = None
    """Additional item properties"""

    rarity: Optional[Rarity] = None
    """Item rarity (optional)"""

    @staticmethod
    def from_dict(obj: Any) -> 'Item':
        assert isinstance(obj, dict)
        id = from_str(obj.get("id"))
        quantity = from_int(obj.get("quantity"))
        level = from_union([from_int, from_none], obj.get("level"))
        properties = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("properties"))
        rarity = from_union([Rarity, from_none], obj.get("rarity"))
        return Item(id, quantity, level, properties, rarity)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = from_str(self.id)
        result["quantity"] = from_int(self.quantity)
        if self.level is not None:
            result["level"] = from_union([from_int, from_none], self.level)
        if self.properties is not None:
            result["properties"] = from_union([lambda x: from_dict(lambda x: x, x), from_none], self.properties)
        if self.rarity is not None:
            result["rarity"] = from_union([lambda x: to_enum(Rarity, x), from_none], self.rarity)
        return result


@dataclass
class InventoryEntity:
    """User inventory information
    
    User inventory information entity
    """
    capacity: int
    """Maximum inventory capacity"""

    gems: int
    """Gem amount"""

    gold: int
    """Gold amount"""

    items: List[Item]
    """List of items in inventory"""

    @staticmethod
    def from_dict(obj: Any) -> 'InventoryEntity':
        assert isinstance(obj, dict)
        capacity = from_int(obj.get("capacity"))
        gems = from_int(obj.get("gems"))
        gold = from_int(obj.get("gold"))
        items = from_list(Item.from_dict, obj.get("items"))
        return InventoryEntity(capacity, gems, gold, items)

    def to_dict(self) -> dict:
        result: dict = {}
        result["capacity"] = from_int(self.capacity)
        result["gems"] = from_int(self.gems)
        result["gold"] = from_int(self.gold)
        result["items"] = from_list(lambda x: to_class(Item, x), self.items)
        return result


@dataclass
class ProfileEntity:
    """User profile information
    
    User profile information entity
    """
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
    def from_dict(obj: Any) -> 'ProfileEntity':
        assert isinstance(obj, dict)
        avatar = from_str(obj.get("avatar"))
        created_at = from_datetime(obj.get("created_at"))
        exp = from_int(obj.get("exp"))
        level = from_int(obj.get("level"))
        nickname = from_str(obj.get("nickname"))
        return ProfileEntity(avatar, created_at, exp, level, nickname)

    def to_dict(self) -> dict:
        result: dict = {}
        result["avatar"] = from_str(self.avatar)
        result["created_at"] = self.created_at.isoformat()
        result["exp"] = from_int(self.exp)
        result["level"] = from_int(self.level)
        result["nickname"] = from_str(self.nickname)
        return result


@dataclass
class UserAggregatesSchema:
    """Complete user data aggregates containing all game content"""

    inventory: InventoryEntity
    """User inventory information"""

    profile: ProfileEntity
    """User profile information"""

    @staticmethod
    def from_dict(obj: Any) -> 'UserAggregatesSchema':
        assert isinstance(obj, dict)
        inventory = InventoryEntity.from_dict(obj.get("inventory"))
        profile = ProfileEntity.from_dict(obj.get("profile"))
        return UserAggregatesSchema(inventory, profile)

    def to_dict(self) -> dict:
        result: dict = {}
        result["inventory"] = to_class(InventoryEntity, self.inventory)
        result["profile"] = to_class(ProfileEntity, self.profile)
        return result


def user_aggregates_schema_from_dict(s: Any) -> UserAggregatesSchema:
    return UserAggregatesSchema.from_dict(s)


def user_aggregates_schema_to_dict(x: UserAggregatesSchema) -> Any:
    return to_class(UserAggregatesSchema, x)
