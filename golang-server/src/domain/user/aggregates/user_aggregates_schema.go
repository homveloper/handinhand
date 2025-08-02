// Code generated from JSON Schema using quicktype. DO NOT EDIT.
// To parse and unparse this JSON data, add this code to your project and do:
//
//    userAggregatesSchema, err := UnmarshalUserAggregatesSchema(bytes)
//    bytes, err = userAggregatesSchema.Marshal()

package entities

import "time"

import "encoding/json"

func UnmarshalUserAggregatesSchema(data []byte) (UserAggregatesSchema, error) {
	var r UserAggregatesSchema
	err := json.Unmarshal(data, &r)
	return r, err
}

func (r *UserAggregatesSchema) Marshal() ([]byte, error) {
	return json.Marshal(r)
}

// Complete user data aggregates containing all game content
type UserAggregatesSchema struct {
	// User inventory information                
	Inventory                    InventoryEntity `json:"inventory"`
	// User profile information                  
	Profile                      ProfileEntity   `json:"profile"`
}

// User inventory information
//
// User inventory information entity
type InventoryEntity struct {
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

// User profile information
//
// User profile information entity
type ProfileEntity struct {
	// Avatar identifier                   
	Avatar                       string    `json:"avatar"`
	// Account creation timestamp          
	CreatedAt                    time.Time `json:"created_at"`
	// Experience points                   
	Exp                          int64     `json:"exp"`
	// User level                          
	Level                        int64     `json:"level"`
	// User nickname                       
	Nickname                     string    `json:"nickname"`
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
