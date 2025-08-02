// Code generated from JSON Schema using quicktype. DO NOT EDIT.
// To parse and unparse this JSON data, add this code to your project and do:
//
//    inventoryEntitySchema, err := UnmarshalInventoryEntitySchema(bytes)
//    bytes, err = inventoryEntitySchema.Marshal()

package entities

import "encoding/json"

func UnmarshalInventoryEntitySchema(data []byte) (InventoryEntitySchema, error) {
	var r InventoryEntitySchema
	err := json.Unmarshal(data, &r)
	return r, err
}

func (r *InventoryEntitySchema) Marshal() ([]byte, error) {
	return json.Marshal(r)
}

// User inventory information entity
type InventoryEntitySchema struct {
	// Maximum inventory capacity       
	Capacity                     int64  `json:"capacity"`
	// Gem amount                       
	Gems                         int64  `json:"gems"`
	// Gold amount                      
	Gold                         int64  `json:"gold"`
	// List of items in inventory       
	Items                        []Item `json:"items"`
}

type Item struct {
	// Item identifier                                  
	ID                           string                 `json:"id"`
	// Item level (optional)                            
	Level                        *int64                 `json:"level,omitempty"`
	// Additional item properties                       
	Properties                   map[string]interface{} `json:"properties,omitempty"`
	// Item quantity                                    
	Quantity                     int64                  `json:"quantity"`
	// Item rarity (optional)                           
	Rarity                       *Rarity                `json:"rarity,omitempty"`
}

// Item rarity (optional)
type Rarity string

const (
	Common    Rarity = "common"
	Epic      Rarity = "epic"
	Legendary Rarity = "legendary"
	Rare      Rarity = "rare"
	Uncommon  Rarity = "uncommon"
)
