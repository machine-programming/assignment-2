"""
Evaluation report functionality for program synthesis.
"""

from typing import Dict, Any, Optional, List


class EvaluationReport:
    """Comprehensive evaluation report for synthesized programs."""
    
    def __init__(self, synthesized_program: str = ""):
        # Synthesized program
        self.synthesized_program: str = synthesized_program
        
        # Compilation/execution status
        self.synthesized: bool = False
        self.compiles: bool = False
        self.executes: bool = False
        
        # Test results
        self.total_tests: int = 0
        self.passed_tests: int = 0
        self.failed_tests: int = 0
        self.test_results: List[Dict[str, Any]] = []
        
        # Output and errors
        self.stdout: str = ""
        self.stderr: str = ""
        self.synthesizer_errors: List[str] = []
        self.compiler_errors: List[str] = []
        self.runtime_errors: List[str] = []
        self.warnings: List[str] = []
        
        # Code quality metrics
        self.has_syntax_errors: bool = False
        self.has_runtime_errors: bool = False
        self.has_logic_errors: bool = False
        
        # Overall assessment
        self.success_rate: float = 0.0
        self.overall_status: str = "unknown"  # "success", "partial", "failed"
    
    def add_test_result(self, test_input: str, expected_output: str, 
                       actual_output: str, status: str, error: Optional[str] = None):
        """Add a test result to the report."""
        test_result = {
            "input": test_input,
            "expected_output": expected_output,
            "actual_output": actual_output,
            "status": status,  # "passed", "failed", "error"
            "error": error
        }
        self.test_results.append(test_result)
        self.total_tests += 1
        
        if status == "passed":
            self.passed_tests += 1
        else:
            self.failed_tests += 1
    
    def add_error(self, error_type: str, error_message: str):
        """Add an error to the report."""
        if error_type == "synthesizer":
            self.synthesizer_errors.append(error_message)
            self.synthesized = False
        elif error_type == "compiler":
            self.compiler_errors.append(error_message)
            self.has_syntax_errors = True
        elif error_type == "runtime":
            self.runtime_errors.append(error_message)
            self.has_runtime_errors = True
        elif error_type == "warning":
            self.warnings.append(error_message)
    
    def finalize(self):
        """Calculate final metrics and status."""
        if self.total_tests > 0:
            self.success_rate = self.passed_tests / self.total_tests
        
        # Determine overall status
        if self.has_syntax_errors or not self.compiles:
            self.overall_status = "failed"
        elif self.success_rate == 1.0:
            self.overall_status = "success"
        elif self.success_rate > 0.0:
            self.overall_status = "partial"
        else:
            self.overall_status = "failed"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "synthesized_program": self.synthesized_program,
            "synthesized": self.synthesized,
            "compiles": self.compiles,
            "executes": self.executes,
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "success_rate": self.success_rate,
            "overall_status": self.overall_status,
            "test_results": self.test_results,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "synthesizer_errors": self.synthesizer_errors,
            "compiler_errors": self.compiler_errors,
            "runtime_errors": self.runtime_errors,
            "warnings": self.warnings,
            "has_syntax_errors": self.has_syntax_errors,
            "has_runtime_errors": self.has_runtime_errors,
            "has_logic_errors": self.has_logic_errors
        }
    
    def __str__(self):
        return f"EvaluationReport(status={self.overall_status}, success_rate={self.success_rate:.2f}, tests={self.passed_tests}/{self.total_tests})"
