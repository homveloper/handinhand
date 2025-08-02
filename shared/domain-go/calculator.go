//go:build wasip1

package main

// Go 1.21+의 wasmexport를 사용한 WASM export 함수들

// 순수 Go 함수들 (WASM 빌드용)
func Add(a, b float64) float64 {
	return a + b
}

func Multiply(a, b float64) float64 {
	return a * b
}

func CalculateTax(amount, taxRate float64) float64 {
	tax := amount * (taxRate / 100)
	total := amount + tax
	return total
}

func AddInt32(a, b int32) int32 {
	return a + b
}

func IsPositive(n float64) int32 {
	if n > 0 {
		return 1 // true
	}
	return 0 // false
}

func Power(base, exponent float64) float64 {
	result := 1.0
	for i := 0; i < int(exponent); i++ {
		result *= base
	}
	return result
}

func CalculateDiscount(price, discountPercent float64) float64 {
	discount := price * (discountPercent / 100)
	return price - discount
}

//go:wasmexport Add
func WasmAdd(a, b float64) float64 {
	return Add(a, b)
}

//go:wasmexport Multiply
func WasmMultiply(a, b float64) float64 {
	return Multiply(a, b)
}

//go:wasmexport CalculateTax
func WasmCalculateTax(amount, taxRate float64) float64 {
	return CalculateTax(amount, taxRate)
}

//go:wasmexport AddInt32
func WasmAddInt32(a, b int32) int32 {
	return AddInt32(a, b)
}

//go:wasmexport IsPositive
func WasmIsPositive(n float64) int32 {
	return IsPositive(n)
}

//go:wasmexport Power
func WasmPower(base, exponent float64) float64 {
	return Power(base, exponent)
}

//go:wasmexport CalculateDiscount
func WasmCalculateDiscount(price, discountPercent float64) float64 {
	return CalculateDiscount(price, discountPercent)
}

// WASI에서는 main 함수가 필요함
func main() {
	// wasmexport 함수들만 사용할 것이므로 빈 main
}