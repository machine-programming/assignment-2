#!/usr/bin/env python3
"""
Test suite for Rust program evaluation function using unittest framework.

This test validates that the evaluate function in synthesizer_rust.py correctly
handles various types of errors and scenarios:
1. Syntax errors
2. Type errors  
3. Runtime errors
4. Timeout errors
5. Partial test failures
6. Complete success
"""

import unittest
import sys
import os
from dataset import ProgramSynthesisDatapoint
from synthesizer_rust import RustProgramSynthesizer


class TestRustEvaluation(unittest.TestCase):
    """Test cases for Rust program evaluation."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.synthesizer = RustProgramSynthesizer()
        self.simple_datapoint = self._create_simple_datapoint()
    
    def _create_simple_datapoint(self):
        """Create a simple test datapoint for testing."""
        return ProgramSynthesisDatapoint({
            "description": "Sum all numbers in a list",
            "input_from": "standard input",
            "output_to": "standard output", 
            "time_limit": 2.0,
            "memory_limit": "256 megabytes",
            "input_spec": "First line contains n, then n integers on the next line",
            "output_spec": "Print the sum of all integers",
            "notes": "Simple test case",
            "sample_inputs": ["1 2 3", "10 20", "5"],  # Just the numbers, no count
            "sample_outputs": ["6", "30", "5"],
            "tags": ["implementation", "math"],
            "src_uid": "test_001",
            "difficulty": 100
        })
    
    def test_syntax_error(self):
        """Test evaluation with syntax error."""
        # Program with syntax error (missing semicolon)
        bad_program = """
fn main() {
    let mut input = String::new();
    std::io::stdin().read_line(&mut input).unwrap()
    let numbers: Vec<i32> = input.trim().split_whitespace()
        .map(|x| x.parse().unwrap())
        .collect();
    let sum: i32 = numbers.iter().sum();
    println!("{}", sum);
}
"""
        
        report = self.synthesizer.evaluate(self.simple_datapoint, bad_program)
        
        # Validate results
        self.assertFalse(report.compiles, "Should not compile due to syntax error")
        self.assertFalse(report.executes, "Should not execute if compilation fails")
        self.assertTrue(report.has_syntax_errors, "Should have syntax errors")
        self.assertGreater(len(report.compiler_errors), 0, "Should have compiler errors")
        self.assertEqual(report.overall_status, "failed", "Overall status should be failed")
        
        print(f"✅ Syntax error test passed - {len(report.compiler_errors)} compiler errors")
    
    def test_type_error(self):
        """Test evaluation with type error."""
        # Program with type error (string vs int)
        bad_program = """
fn main() {
    let mut input = String::new();
    std::io::stdin().read_line(&mut input).unwrap();
    let numbers: Vec<i32> = input.trim().split_whitespace()
        .map(|x| x.parse().unwrap())
        .collect();
    let sum: i32 = numbers.iter().sum();
    println!("{}", sum + "invalid");  // Type error: can't add i32 and &str
}
"""
        
        report = self.synthesizer.evaluate(self.simple_datapoint, bad_program)
        
        # Validate results
        self.assertFalse(report.compiles, "Should not compile due to type error")
        self.assertFalse(report.executes, "Should not execute if compilation fails")
        self.assertTrue(report.has_syntax_errors, "Should have syntax errors")
        self.assertGreater(len(report.compiler_errors), 0, "Should have compiler errors")
        self.assertEqual(report.overall_status, "failed", "Overall status should be failed")
        
        print(f"✅ Type error test passed - {len(report.compiler_errors)} compiler errors")
    
    def test_runtime_error(self):
        """Test evaluation with runtime error."""
        # Program that compiles but has runtime error (index out of bounds)
        bad_program = """
fn main() {
    let mut input = String::new();
    std::io::stdin().read_line(&mut input).unwrap();
    let numbers: Vec<i32> = input.trim().split_whitespace()
        .map(|x| x.parse().unwrap())
        .collect();
    
    // This will panic with index out of bounds
    let sum: i32 = numbers.iter().sum();
    let first = numbers[10];  // This will panic if numbers has less than 11 elements
    println!("{}", sum);
}
"""
        
        report = self.synthesizer.evaluate(self.simple_datapoint, bad_program)
        
        # Validate results
        self.assertTrue(report.compiles, "Should compile successfully")
        self.assertTrue(report.executes, "Should attempt execution")
        self.assertTrue(report.has_runtime_errors, "Should have runtime errors")
        self.assertGreater(len(report.runtime_errors), 0, "Should have runtime errors")
        self.assertIn(report.overall_status, ["failed", "partial"], "Overall status should be failed or partial")
        
        print(f"✅ Runtime error test passed - {len(report.runtime_errors)} runtime errors, {report.passed_tests}/{report.total_tests} tests passed")
    
    def test_timeout(self):
        """Test evaluation with timeout."""
        # Create a datapoint with very short timeout
        timeout_datapoint = ProgramSynthesisDatapoint({
            "description": "Sum all numbers in a list",
            "input_from": "standard input",
            "output_to": "standard output", 
            "time_limit": 0.1,  # Very short timeout
            "memory_limit": "256 megabytes",
            "input_spec": "First line contains n, then n integers on the next line",
            "output_spec": "Print the sum of all integers",
            "notes": "Simple test case",
            "sample_inputs": ["1 2 3"],
            "sample_outputs": ["6"],
            "tags": ["implementation", "math"],
            "src_uid": "test_001",
            "difficulty": 100
        })
        
        # Program that will timeout (infinite loop)
        bad_program = """
fn main() {
    let mut input = String::new();
    std::io::stdin().read_line(&mut input).unwrap();
    let numbers: Vec<i32> = input.trim().split_whitespace()
        .map(|x| x.parse().unwrap())
        .collect();
    
    // Infinite loop to cause timeout
    loop {
        // This will run forever
    }
}
"""
        
        report = self.synthesizer.evaluate(timeout_datapoint, bad_program)
        
        # Validate results
        self.assertTrue(report.compiles, "Should compile successfully")
        self.assertTrue(report.executes, "Should attempt execution")
        self.assertGreater(len(report.runtime_errors), 0, "Should have timeout errors")
        self.assertTrue(any("timed out" in error.lower() for error in report.runtime_errors), "Should have timeout error")
        self.assertIn(report.overall_status, ["failed", "partial"], "Overall status should be failed or partial")
        
        print(f"✅ Timeout test passed - {len(report.runtime_errors)} runtime errors, {report.passed_tests}/{report.total_tests} tests passed")
    
    def test_partial_failure(self):
        """Test evaluation with partial test failure."""
        # Program that works for some inputs but not others (only works for even-length arrays)
        bad_program = """
fn main() {
    let mut input = String::new();
    std::io::stdin().read_line(&mut input).unwrap();
    let numbers: Vec<i32> = input.trim().split_whitespace()
        .map(|x| x.parse().unwrap())
        .collect();
    
    // Only works correctly for even-length arrays, adds 1 for odd-length
    let sum: i32 = numbers.iter().sum();
    if numbers.len() % 2 == 0 {
        println!("{}", sum);
    } else {
        println!("{}", sum + 1);
    }
}
"""
        
        report = self.synthesizer.evaluate(self.simple_datapoint, bad_program)
        
        # Validate results
        self.assertTrue(report.compiles, "Should compile successfully")
        self.assertTrue(report.executes, "Should execute successfully")
        self.assertFalse(report.has_syntax_errors, "Should not have syntax errors")
        self.assertFalse(report.has_runtime_errors, "Should not have runtime errors")
        self.assertLess(report.passed_tests, report.total_tests, "Should have some failed tests")
        self.assertGreater(report.passed_tests, 0, "Should have some passed tests")
        self.assertEqual(report.overall_status, "partial", "Overall status should be partial")
        self.assertGreater(report.success_rate, 0, "Success rate should be greater than 0")
        self.assertLess(report.success_rate, 1.0, "Success rate should be less than 1.0")
        
        print(f"✅ Partial failure test passed - {report.passed_tests}/{report.total_tests} tests passed ({report.success_rate:.2%})")
        
        # Print test details
        for i, test in enumerate(report.test_results):
            status_icon = "✅" if test["status"] == "passed" else "❌"
            print(f"   Test {i+1}: {status_icon} Input: {test['input']} | Expected: {test['expected_output']} | Got: {test['actual_output']}")
    
    def test_success(self):
        """Test evaluation with complete success."""
        # Correct program
        good_program = """
fn main() {
    let mut input = String::new();
    std::io::stdin().read_line(&mut input).unwrap();
    let numbers: Vec<i32> = input.trim().split_whitespace()
        .map(|x| x.parse().unwrap())
        .collect();
    let sum: i32 = numbers.iter().sum();
    println!("{}", sum);
}
"""
        
        report = self.synthesizer.evaluate(self.simple_datapoint, good_program)
        
        # Validate results
        self.assertTrue(report.compiles, "Should compile successfully")
        self.assertTrue(report.executes, "Should execute successfully")
        self.assertFalse(report.has_syntax_errors, "Should not have syntax errors")
        self.assertFalse(report.has_runtime_errors, "Should not have runtime errors")
        self.assertEqual(report.passed_tests, report.total_tests, "Should pass all tests")
        self.assertEqual(report.overall_status, "success", "Overall status should be success")
        self.assertEqual(report.success_rate, 1.0, "Success rate should be 100%")
        
        print(f"✅ Complete success test passed - {report.passed_tests}/{report.total_tests} tests passed ({report.success_rate:.2%})")
    
    def test_compilation_failure(self):
        """Test evaluation with compilation failure."""
        # Program that will cause compilation to fail (invalid syntax)
        bad_program = """
fn main() {
    let mut input = String::new();
    std::io::stdin().read_line(&mut input).unwrap();
    let numbers: Vec<i32> = input.trim().split_whitespace()
        .map(|x| x.parse().unwrap())
        .collect();
    
    // This will cause a compilation error due to invalid syntax
    let sum: i32 = numbers.iter().sum();
    println!("{}", sum);
    
    // Invalid syntax that will cause compilation to fail
    let invalid = if true { 1 } else { 2 } 3;  // Missing semicolon and extra token
}
"""
        
        report = self.synthesizer.evaluate(self.simple_datapoint, bad_program)
        
        # Validate results
        self.assertFalse(report.compiles, "Should not compile due to syntax error")
        self.assertFalse(report.executes, "Should not execute if compilation fails")
        self.assertEqual(report.overall_status, "failed", "Overall status should be failed")
        
        print(f"✅ Compilation failure test passed - Compiles: {report.compiles}, {len(report.compiler_errors)} compiler errors")


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestRustEvaluation)
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)