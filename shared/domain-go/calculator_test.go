package main

import (
	"testing"
)

func TestAdd(t *testing.T) {
	tests := []struct {
		name     string
		a        float64
		b        float64
		expected float64
	}{
		{
			name:     "positive numbers",
			a:        5.0,
			b:        3.0,
			expected: 8.0,
		},
		{
			name:     "negative numbers",
			a:        -5.0,
			b:        -3.0,
			expected: -8.0,
		},
		{
			name:     "mixed numbers",
			a:        10.0,
			b:        -3.0,
			expected: 7.0,
		},
		{
			name:     "decimal numbers",
			a:        5.5,
			b:        2.5,
			expected: 8.0,
		},
		{
			name:     "zero values",
			a:        0.0,
			b:        0.0,
			expected: 0.0,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := Add(tt.a, tt.b)
			if result != tt.expected {
				t.Errorf("Add(%f, %f) = %f; want %f", tt.a, tt.b, result, tt.expected)
			}
		})
	}
}

func TestMultiply(t *testing.T) {
	tests := []struct {
		name     string
		a        float64
		b        float64
		expected float64
	}{
		{
			name:     "positive numbers",
			a:        5.0,
			b:        3.0,
			expected: 15.0,
		},
		{
			name:     "negative numbers",
			a:        -5.0,
			b:        -3.0,
			expected: 15.0,
		},
		{
			name:     "mixed numbers",
			a:        10.0,
			b:        -3.0,
			expected: -30.0,
		},
		{
			name:     "with zero",
			a:        5.0,
			b:        0.0,
			expected: 0.0,
		},
		{
			name:     "decimal numbers",
			a:        2.5,
			b:        4.0,
			expected: 10.0,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := Multiply(tt.a, tt.b)
			if result != tt.expected {
				t.Errorf("Multiply(%f, %f) = %f; want %f", tt.a, tt.b, result, tt.expected)
			}
		})
	}
}

func TestCalculateTax(t *testing.T) {
	tests := []struct {
		name          string
		amount        float64
		taxRate       float64
		expectedTotal float64
	}{
		{
			name:          "10% tax",
			amount:        100.0,
			taxRate:       10.0,
			expectedTotal: 110.0,
		},
		{
			name:          "20% tax",
			amount:        200.0,
			taxRate:       20.0,
			expectedTotal: 240.0,
		},
		{
			name:          "0% tax",
			amount:        100.0,
			taxRate:       0.0,
			expectedTotal: 100.0,
		},
		{
			name:          "decimal tax rate",
			amount:        150.0,
			taxRate:       7.5,
			expectedTotal: 161.25,
		},
		{
			name:          "large amount",
			amount:        10000.0,
			taxRate:       15.0,
			expectedTotal: 11500.0,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := CalculateTax(tt.amount, tt.taxRate)

			if result != tt.expectedTotal {
				t.Errorf("CalculateTax(%f, %f) = %f; want %f", tt.amount, tt.taxRate, result, tt.expectedTotal)
			}
		})
	}
}

func TestAddInt32(t *testing.T) {
	tests := []struct {
		name     string
		a        int32
		b        int32
		expected int32
	}{
		{
			name:     "positive integers",
			a:        10,
			b:        20,
			expected: 30,
		},
		{
			name:     "negative integers",
			a:        -10,
			b:        -20,
			expected: -30,
		},
		{
			name:     "mixed integers",
			a:        15,
			b:        -5,
			expected: 10,
		},
		{
			name:     "zero values",
			a:        0,
			b:        0,
			expected: 0,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := AddInt32(tt.a, tt.b)
			if result != tt.expected {
				t.Errorf("AddInt32(%d, %d) = %d; want %d", tt.a, tt.b, result, tt.expected)
			}
		})
	}
}

func TestIsPositive(t *testing.T) {
	tests := []struct {
		name     string
		n        float64
		expected int32
	}{
		{
			name:     "positive number",
			n:        5.0,
			expected: 1,
		},
		{
			name:     "negative number",
			n:        -5.0,
			expected: 0,
		},
		{
			name:     "zero",
			n:        0.0,
			expected: 0,
		},
		{
			name:     "positive decimal",
			n:        0.1,
			expected: 1,
		},
		{
			name:     "negative decimal",
			n:        -0.1,
			expected: 0,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := IsPositive(tt.n)
			if result != tt.expected {
				t.Errorf("IsPositive(%f) = %d; want %d", tt.n, result, tt.expected)
			}
		})
	}
}

func TestPower(t *testing.T) {
	tests := []struct {
		name     string
		base     float64
		exponent float64
		expected float64
	}{
		{
			name:     "2^3",
			base:     2.0,
			exponent: 3.0,
			expected: 8.0,
		},
		{
			name:     "5^0",
			base:     5.0,
			exponent: 0.0,
			expected: 1.0,
		},
		{
			name:     "10^2",
			base:     10.0,
			exponent: 2.0,
			expected: 100.0,
		},
		{
			name:     "3^4",
			base:     3.0,
			exponent: 4.0,
			expected: 81.0,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := Power(tt.base, tt.exponent)
			if result != tt.expected {
				t.Errorf("Power(%f, %f) = %f; want %f", tt.base, tt.exponent, result, tt.expected)
			}
		})
	}
}

func TestCalculateDiscount(t *testing.T) {
	tests := []struct {
		name            string
		price           float64
		discountPercent float64
		expected        float64
	}{
		{
			name:            "10% discount",
			price:           100.0,
			discountPercent: 10.0,
			expected:        90.0,
		},
		{
			name:            "25% discount",
			price:           200.0,
			discountPercent: 25.0,
			expected:        150.0,
		},
		{
			name:            "0% discount",
			price:           100.0,
			discountPercent: 0.0,
			expected:        100.0,
		},
		{
			name:            "50% discount",
			price:           80.0,
			discountPercent: 50.0,
			expected:        40.0,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := CalculateDiscount(tt.price, tt.discountPercent)
			if result != tt.expected {
				t.Errorf("CalculateDiscount(%f, %f) = %f; want %f", tt.price, tt.discountPercent, result, tt.expected)
			}
		})
	}
}

// 벤치마크 테스트
func BenchmarkAdd(b *testing.B) {
	for i := 0; i < b.N; i++ {
		Add(100.0, 200.0)
	}
}

func BenchmarkMultiply(b *testing.B) {
	for i := 0; i < b.N; i++ {
		Multiply(100.0, 200.0)
	}
}

func BenchmarkCalculateTax(b *testing.B) {
	for i := 0; i < b.N; i++ {
		CalculateTax(1000.0, 15.0)
	}
}

func BenchmarkPower(b *testing.B) {
	for i := 0; i < b.N; i++ {
		Power(2.0, 10.0)
	}
}
