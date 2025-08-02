//go:build wasm && js

package main

import (
	"fmt"
	"syscall/js"
)

// 간단한 계산기 도메인 로직
type Calculator struct{}

// Add 함수 - 두 숫자를 더하는 간단한 예제
func (c *Calculator) Add(a, b float64) float64 {
	return a + b
}

// Multiply 함수 - 두 숫자를 곱하는 예제
func (c *Calculator) Multiply(a, b float64) float64 {
	return a * b
}

// 복잡한 계산 예제 - 여러 도메인 로직이 조합된 경우
func (c *Calculator) CalculateTax(amount float64, taxRate float64) map[string]float64 {
	tax := amount * (taxRate / 100)
	total := amount + tax

	return map[string]float64{
		"amount":  amount,
		"taxRate": taxRate,
		"tax":     tax,
		"total":   total,
	}
}

// JavaScript 래퍼 함수들
func addWrapper(this js.Value, args []js.Value) interface{} {
	if len(args) < 2 {
		return js.ValueOf("Error: Add function requires 2 arguments")
	}

	a := args[0].Float()
	b := args[1].Float()

	calc := &Calculator{}
	result := calc.Add(a, b)

	return js.ValueOf(result)
}

func multiplyWrapper(this js.Value, args []js.Value) interface{} {
	if len(args) < 2 {
		return js.ValueOf("Error: Multiply function requires 2 arguments")
	}

	a := args[0].Float()
	b := args[1].Float()

	calc := &Calculator{}
	result := calc.Multiply(a, b)

	return js.ValueOf(result)
}

func calculateTaxWrapper(this js.Value, args []js.Value) interface{} {
	if len(args) < 2 {
		return js.ValueOf("Error: CalculateTax function requires 2 arguments")
	}

	amount := args[0].Float()
	taxRate := args[1].Float()

	calc := &Calculator{}
	result := calc.CalculateTax(amount, taxRate)

	// Go map을 JavaScript object로 변환
	jsResult := js.ValueOf(map[string]interface{}{
		"amount":  result["amount"],
		"taxRate": result["taxRate"],
		"tax":     result["tax"],
		"total":   result["total"],
	})

	return jsResult
}

func main() {
	// JavaScript 전역 객체에 Calculator 모듈 등록
	js.Global().Set("CalculatorWASM", js.ValueOf(map[string]interface{}{
		"add":          js.FuncOf(addWrapper),
		"multiply":     js.FuncOf(multiplyWrapper),
		"calculateTax": js.FuncOf(calculateTaxWrapper),
	}))

	fmt.Println("Go WASM Calculator module loaded!")

	// 프로그램이 종료되지 않도록 대기
	<-make(chan bool)
}
