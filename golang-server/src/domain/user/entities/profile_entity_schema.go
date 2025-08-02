// Code generated from JSON Schema using quicktype. DO NOT EDIT.
// To parse and unparse this JSON data, add this code to your project and do:
//
//    profileEntitySchema, err := UnmarshalProfileEntitySchema(bytes)
//    bytes, err = profileEntitySchema.Marshal()

package entities

import "time"

import "encoding/json"

func UnmarshalProfileEntitySchema(data []byte) (ProfileEntitySchema, error) {
	var r ProfileEntitySchema
	err := json.Unmarshal(data, &r)
	return r, err
}

func (r *ProfileEntitySchema) Marshal() ([]byte, error) {
	return json.Marshal(r)
}

// User profile information entity
type ProfileEntitySchema struct {
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
