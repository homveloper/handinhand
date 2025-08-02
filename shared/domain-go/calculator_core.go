//go:build !wasip1

package main

// 순수 Go 함수들 - 일반 Go 빌드와 테스트에서 사용

// Add returns the sum of two numbers
func Add(a, b float64) float64 {
	return a + b
}

// Multiply returns the product of two numbers
func Multiply(a, b float64) float64 {
	return a * b
}

// CalculateTax calculates the total amount including tax
func CalculateTax(amount, taxRate float64) float64 {
	tax := amount * (taxRate / 100)
	total := amount + tax
	return total
}

// AddInt32 returns the sum of two 32-bit integers
func AddInt32(a, b int32) int32 {
	return a + b
}

// IsPositive returns 1 if the number is positive, 0 otherwise
func IsPositive(n float64) int32 {
	if n > 0 {
		return 1 // true
	}
	return 0 // false
}

// Power calculates base raised to the power of exponent
func Power(base, exponent float64) float64 {
	result := 1.0
	for i := 0; i < int(exponent); i++ {
		result *= base
	}
	return result
}

// CalculateDiscount calculates the price after applying a discount percentage
func CalculateDiscount(price, discountPercent float64) float64 {
	discount := price * (discountPercent / 100)
	return price - discount
}