from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, TypeVar, Callable, Type, cast


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
    """User inventory information entity"""

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


def inventory_entity_from_dict(s: Any) -> InventoryEntity:
    return InventoryEntity.from_dict(s)


def inventory_entity_to_dict(x: InventoryEntity) -> Any:
    return to_class(InventoryEntity, x)
