// Code generated from JSON Schema using quicktype. DO NOT EDIT.
// To parse and unparse this JSON data, add this code to your project and do:
//
//    serverConfigSchema, err := UnmarshalServerConfigSchema(bytes)
//    bytes, err = serverConfigSchema.Marshal()

package config

import "encoding/json"

func UnmarshalServerConfigSchema(data []byte) (ServerConfigSchema, error) {
	var r ServerConfigSchema
	err := json.Unmarshal(data, &r)
	return r, err
}

func (r *ServerConfigSchema) Marshal() ([]byte, error) {
	return json.Marshal(r)
}

// Configuration schema for all 4 language servers (Node.js, Python, Go, C#)
type ServerConfigSchema struct {
	API                   API         `json:"api"`
	Cors                  Cors        `json:"cors"`
	// Enable debug mode              
	Debug                 bool        `json:"debug"`
	// Current environment            
	Environment           Environment `json:"environment"`
	Jsonrpc               Jsonrpc     `json:"jsonrpc"`
	Logging               Logging     `json:"logging"`
	Nginx                 Nginx       `json:"nginx"`
	Redis                 Redis       `json:"redis"`
	Servers               Servers     `json:"servers"`
	SSE                   SSE         `json:"sse"`
}

type API struct {
	// API base path                         
	BasePath                       string    `json:"base_path"`
	RateLimit                      RateLimit `json:"rate_limit"`
	// Enable Swagger documentation          
	SwaggerEnabled                 bool      `json:"swagger_enabled"`
	// API version                           
	Version                        string    `json:"version"`
}

type RateLimit struct {
	// Maximum requests per window            
	MaxRequests                         int64 `json:"max_requests"`
	// Rate limit window in milliseconds      
	WindowMS                            int64 `json:"window_ms"`
}

type Cors struct {
	// Allow credentials in CORS requests                
	AllowCredentials                     bool            `json:"allow_credentials"`
	// Allowed HTTP headers                              
	AllowedHeaders                       []string        `json:"allowed_headers"`
	// Allowed HTTP methods                              
	AllowedMethods                       []AllowedMethod `json:"allowed_methods"`
	// Allowed CORS origins                              
	AllowedOrigins                       []string        `json:"allowed_origins"`
}

type Jsonrpc struct {
	// Maximum batch request size             
	BatchLimit                        int64   `json:"batch_limit"`
	// Request timeout in milliseconds        
	Timeout                           int64   `json:"timeout"`
	// JSON-RPC version                       
	Version                           Version `json:"version"`
}

type Logging struct {
	// Enable console logging       
	ConsoleEnabled           bool   `json:"console_enabled"`
	// Enable file logging          
	FileEnabled              bool   `json:"file_enabled"`
	// Log format                   
	Format                   Format `json:"format"`
	// Logging level                
	Level                    Level  `json:"level"`
}

type Nginx struct {
	// Health check endpoint path       
	HealthCheckPath              string `json:"health_check_path"`
	// NGINX listen port                
	Port                         int64  `json:"port"`
	// NGINX upstream name              
	UpstreamName                 string `json:"upstream_name"`
}

type Redis struct {
	// Redis database number                     
	DB                                   int64   `json:"db"`
	// Redis host address                        
	Host                                 string  `json:"host"`
	// Maximum retry attempts per request        
	MaxRetriesPerRequest                 *int64  `json:"max_retries_per_request,omitempty"`
	// Redis password (optional)                 
	Password                             *string `json:"password,omitempty"`
	// Redis port number                         
	Port                                 int64   `json:"port"`
	// Retry delay in milliseconds               
	RetryDelayOnFailover                 *int64  `json:"retry_delay_on_failover,omitempty"`
}

type SSE struct {
	// SSE heartbeat interval in milliseconds      
	HeartbeatInterval                        int64 `json:"heartbeat_interval"`
	// Maximum SSE connections                     
	MaxConnections                           int64 `json:"max_connections"`
	// SSE reconnect timeout in milliseconds       
	ReconnectTimeout                         int64 `json:"reconnect_timeout"`
}

type Servers struct {
	Csharp ServerInfo `json:"csharp"`
	Golang ServerInfo `json:"golang"`
	Nodejs ServerInfo `json:"nodejs"`
	Python ServerInfo `json:"python"`
}

type ServerInfo struct {
	// Server host address       
	Host                  string `json:"host"`
	// Server name               
	Name                  string `json:"name"`
	// Server port number        
	Port                  int64  `json:"port"`
}

type AllowedMethod string

const (
	Delete  AllowedMethod = "DELETE"
	Get     AllowedMethod = "GET"
	Head    AllowedMethod = "HEAD"
	Options AllowedMethod = "OPTIONS"
	Patch   AllowedMethod = "PATCH"
	Post    AllowedMethod = "POST"
	Put     AllowedMethod = "PUT"
)

// Current environment
type Environment string

const (
	Development Environment = "development"
	Production  Environment = "production"
	Testing     Environment = "testing"
)

// JSON-RPC version
type Version string

const (
	The20 Version = "2.0"
)

// Log format
type Format string

const (
	JSON Format = "json"
	Text Format = "text"
)

// Logging level
type Level string

const (
	Debug Level = "debug"
	Error Level = "error"
	Info  Level = "info"
	Warn  Level = "warn"
)
