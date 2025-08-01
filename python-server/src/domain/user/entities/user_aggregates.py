"""
UserAggregates 비즈니스 로직 구현
JSON Schema 자동 생성 모델을 기반으로 한 실제 도메인 엔티티
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field

# 자동 생성된 스키마 모델들 임포트
from .user_aggregates_schema import (
    UserAggregatesSchema as SchemaUserAggregates,
    ProfileEntity as SchemaProfileEntity,
    InventoryEntity as SchemaInventoryEntity,
    Item as SchemaItem,
    Rarity
)


@dataclass
class Item:
    """아이템 엔티티 - 비즈니스 로직 포함"""
    id: str
    quantity: int
    level: Optional[int] = None
    properties: Optional[Dict[str, Any]] = None
    rarity: Optional[Rarity] = None
    
    @classmethod
    def from_schema(cls, schema_item: SchemaItem) -> 'Item':
        """스키마 객체에서 비즈니스 객체로 변환"""
        return cls(
            id=schema_item.id,
            quantity=schema_item.quantity,
            level=schema_item.level,
            properties=schema_item.properties,
            rarity=schema_item.rarity
        )
    
    def to_schema(self) -> SchemaItem:
        """비즈니스 객체에서 스키마 객체로 변환"""
        return SchemaItem(
            id=self.id,
            quantity=self.quantity,
            level=self.level,
            properties=self.properties,
            rarity=self.rarity
        )
    
    def is_stackable(self) -> bool:
        """아이템이 스택 가능한지 확인"""
        return self.quantity > 1
    
    def get_total_value(self) -> int:
        """아이템의 총 가치 계산"""
        rarity_multiplier = {
            Rarity.COMMON: 1,
            Rarity.UNCOMMON: 2,
            Rarity.RARE: 5,
            Rarity.EPIC: 10,
            Rarity.LEGENDARY: 25
        }
        
        level = self.level or 1
        multiplier = rarity_multiplier.get(self.rarity, 1) if self.rarity else 1
        
        return level * multiplier * self.quantity
    
    def can_upgrade(self) -> bool:
        """아이템 업그레이드 가능 여부"""
        return self.level is not None and self.level < 100


@dataclass
class InventoryEntity:
    """인벤토리 엔티티 - 비즈니스 로직 포함"""
    items: List[Item] = field(default_factory=list)
    gold: int = 0
    gems: int = 0
    capacity: int = 50
    
    @classmethod
    def from_schema(cls, schema_inventory: SchemaInventoryEntity) -> 'InventoryEntity':
        """스키마 객체에서 비즈니스 객체로 변환"""
        items = [Item.from_schema(item) for item in schema_inventory.items]
        return cls(
            items=items,
            gold=schema_inventory.gold,
            gems=schema_inventory.gems,
            capacity=schema_inventory.capacity
        )
    
    def to_schema(self) -> SchemaInventoryEntity:
        """비즈니스 객체에서 스키마 객체로 변환"""
        schema_items = [item.to_schema() for item in self.items]
        return SchemaInventoryEntity(
            items=schema_items,
            gold=self.gold,
            gems=self.gems,
            capacity=self.capacity
        )
    
    def is_full(self) -> bool:
        """인벤토리가 가득 찼는지 확인"""
        return len(self.items) >= self.capacity
    
    def get_available_slots(self) -> int:
        """사용 가능한 슬롯 수"""
        return self.capacity - len(self.items)
    
    def find_item_by_id(self, item_id: str) -> Optional[Item]:
        """ID로 아이템 찾기"""
        for item in self.items:
            if item.id == item_id:
                return item
        return None
    
    def add_item(self, item: Item) -> bool:
        """아이템 추가 (용량 체크 포함)"""
        if self.is_full():
            return False
            
        # 기존 아이템과 스택 가능한지 확인
        existing_item = self.find_item_by_id(item.id)
        if existing_item and existing_item.is_stackable():
            existing_item.quantity += item.quantity
            return True
        
        self.items.append(item)
        return True
    
    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """아이템 제거"""
        item = self.find_item_by_id(item_id)
        if not item:
            return False
            
        if item.quantity <= quantity:
            self.items = [i for i in self.items if i.id != item_id]
        else:
            item.quantity -= quantity
            
        return True
    
    def get_total_value(self) -> int:
        """인벤토리 총 가치"""
        return sum(item.get_total_value() for item in self.items)
    
    def has_currency(self, gold: int = 0, gems: int = 0) -> bool:
        """충분한 화폐가 있는지 확인"""
        return self.gold >= gold and self.gems >= gems
    
    def spend_currency(self, gold: int = 0, gems: int = 0) -> bool:
        """화폐 소비"""
        if not self.has_currency(gold, gems):
            return False
            
        self.gold -= gold
        self.gems -= gems
        return True


@dataclass
class ProfileEntity:
    """프로필 엔티티 - 비즈니스 로직 포함"""
    nickname: str
    level: int = 1
    exp: int = 0
    avatar: str = "default"
    created_at: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def from_schema(cls, schema_profile: SchemaProfileEntity) -> 'ProfileEntity':
        """스키마 객체에서 비즈니스 객체로 변환"""
        return cls(
            nickname=schema_profile.nickname,
            level=schema_profile.level,
            exp=schema_profile.exp,
            avatar=schema_profile.avatar,
            created_at=schema_profile.created_at
        )
    
    def to_schema(self) -> SchemaProfileEntity:
        """비즈니스 객체에서 스키마 객체로 변환"""
        return SchemaProfileEntity(
            nickname=self.nickname,
            level=self.level,
            exp=self.exp,
            avatar=self.avatar,
            created_at=self.created_at
        )
    
    def get_exp_to_next_level(self) -> int:
        """다음 레벨까지 필요한 경험치"""
        return self.get_exp_required_for_level(self.level + 1) - self.exp
    
    def get_exp_required_for_level(self, level: int) -> int:
        """특정 레벨에 필요한 총 경험치"""
        return level * 1000  # 간단한 공식: 레벨 * 1000
    
    def can_level_up(self) -> bool:
        """레벨업 가능 여부"""
        return self.exp >= self.get_exp_required_for_level(self.level + 1)
    
    def add_exp(self, exp_amount: int) -> int:
        """경험치 추가 및 레벨업 처리"""
        self.exp += exp_amount
        levels_gained = 0
        
        while self.can_level_up() and self.level < 100:
            self.level += 1
            levels_gained += 1
            
        return levels_gained
    
    def get_account_age_days(self) -> int:
        """계정 생성 후 경과 일수"""
        return (datetime.now() - self.created_at).days
    
    def is_new_player(self) -> bool:
        """신규 플레이어 여부 (7일 이내)"""
        return self.get_account_age_days() <= 7


@dataclass
class UserAggregates:
    """사용자 전체 데이터 집합체 - 비즈니스 로직 포함"""
    profile: ProfileEntity
    inventory: InventoryEntity
    
    @classmethod
    def from_schema(cls, schema_user: SchemaUserAggregates) -> 'UserAggregates':
        """스키마 객체에서 비즈니스 객체로 변환"""
        profile = ProfileEntity.from_schema(schema_user.profile)
        inventory = InventoryEntity.from_schema(schema_user.inventory)
        return cls(profile=profile, inventory=inventory)
    
    def to_schema(self) -> SchemaUserAggregates:
        """비즈니스 객체에서 스키마 객체로 변환"""
        return SchemaUserAggregates(
            profile=self.profile.to_schema(),
            inventory=self.inventory.to_schema()
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환 (JSON 직렬화용)"""
        return self.to_schema().to_dict()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserAggregates':
        """딕셔너리에서 객체 생성 (JSON 역직렬화용)"""
        schema_user = SchemaUserAggregates.from_dict(data)
        return cls.from_schema(schema_user)
    
    def process_level_up(self, exp_amount: int) -> Dict[str, Any]:
        """레벨업 처리 및 보상 지급"""
        old_level = self.profile.level
        levels_gained = self.profile.add_exp(exp_amount)
        
        if levels_gained > 0:
            # 레벨업 보상 지급
            gold_reward = levels_gained * 500
            gem_reward = levels_gained * 10
            
            self.inventory.gold += gold_reward
            self.inventory.gems += gem_reward
            
            return {
                'levels_gained': levels_gained,
                'old_level': old_level,
                'new_level': self.profile.level,
                'rewards': {
                    'gold': gold_reward,
                    'gems': gem_reward
                }
            }
        
        return {'levels_gained': 0}
    
    def purchase_item(self, item: Item, gold_cost: int, gem_cost: int = 0) -> bool:
        """아이템 구매"""
        if not self.inventory.has_currency(gold_cost, gem_cost):
            return False
            
        if self.inventory.is_full():
            return False
            
        if self.inventory.spend_currency(gold_cost, gem_cost):
            return self.inventory.add_item(item)
            
        return False
    
    def get_player_stats(self) -> Dict[str, Any]:
        """플레이어 통계 정보"""
        return {
            'level': self.profile.level,
            'exp': self.profile.exp,
            'exp_to_next_level': self.profile.get_exp_to_next_level(),
            'gold': self.inventory.gold,
            'gems': self.inventory.gems,
            'inventory_slots_used': len(self.inventory.items),
            'inventory_capacity': self.inventory.capacity,
            'total_inventory_value': self.inventory.get_total_value(),
            'account_age_days': self.profile.get_account_age_days(),
            'is_new_player': self.profile.is_new_player()
        }
    
    @classmethod
    def create_new_user(cls, user_id: str, nickname: str) -> 'UserAggregates':
        """새 사용자 생성"""
        profile = ProfileEntity(
            nickname=nickname,
            level=1,
            exp=0,
            avatar="default",
            created_at=datetime.now()
        )
        
        inventory = InventoryEntity(
            items=[],
            gold=1000,  # 초기 골드
            gems=50,    # 초기 젬
            capacity=50  # 초기 용량
        )
        
        return cls(profile=profile, inventory=inventory)