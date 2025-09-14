import re
import time
import random
from typing import Dict, Any, Optional
from dataset import ProgramSynthesisDatapoint
from model import GeminiClient
from logger import SynthesisLogger
from report import EvaluationReport


class ProgramSynthesizer:
    """Parent class for program synthesis using different prompting methods."""
    
    def __init__(self, target_language: str, prompting_method: str, 
                 model_name: str = "gemini-1.5-flash", api_key: Optional[str] = None,
                 logger: Optional[SynthesisLogger] = None):
        """
        Initialize program synthesizer.
        
        Args:
            target_language: Target programming language
            prompting_method: Method to use for prompting
            model_name: Name of the Gemini model
            api_key: API key (optional, will use environment variable)
            logger: SynthesisLogger instance (optional, will create default if None)
        """
        self.target_language = target_language
        self.prompting_method = prompting_method
        self.model_name = model_name
        
        # Initialize Gemini client
        self.model = GeminiClient(model_name, api_key)
        
        # Use provided logger or create default one
        self.logger = logger if logger is not None else SynthesisLogger()
        
        # Store configuration
        self.config = {
            "target_language": target_language,
            "prompting_method": prompting_method,
            "model_name": model_name
        }

    def synthesize(self, datapoint: ProgramSynthesisDatapoint) -> str:
        """
        Synthesize a program for the given datapoint using the configured prompting method.
        
        Args:
            datapoint: The problem datapoint to synthesize a solution for
            
        Returns:
            Synthesized program as string
        """
        try:
            # Route to appropriate prompting method
            if self.prompting_method == "zero_shot":
                synthesized_program = self.zero_shot(datapoint)
            elif self.prompting_method == "two_step_chain_of_thought":
                synthesized_program = self.two_step_chain_of_thought(datapoint)
            elif self.prompting_method == "iterative_refinement":
                synthesized_program = self.iterative_refinement_with_feedback(datapoint)
            elif self.prompting_method == "YOUR_CUSTOM_PROMPTING_METHOD":
                ################################################################################
                #                                                                              #
                # TODO: Part 2d. Implement your custom prompting method.                       #
                #                                                                              #
                ################################################################################
                synthesized_program = self.YOUR_CUSTOM_PROMPTING_METHOD(datapoint)
            else:
                raise ValueError(f"Unknown prompting method: {self.prompting_method}")
            
            # Log successful synthesis
            self.logger.log_synthesis(datapoint, self.config, synthesized_program, success=True)
            
            return synthesized_program
            
        except Exception as e:
            # Log failed synthesis
            self.logger.log_synthesis(datapoint, self.config, "", success=False, error=str(e))
            raise

    def zero_shot(self, datapoint: ProgramSynthesisDatapoint) -> str:
        ################################################################################
        #                                                                              #
        # TODO: Part 2a. Implement your zero-shot prompting method.                    #
        #                                                                              #
        ################################################################################
        return ""

    def two_step_chain_of_thought(self, datapoint: ProgramSynthesisDatapoint) -> str:
        ################################################################################
        #                                                                              #
        # TODO: Part 2b. Implement your two-step chain-of-thought prompting method.    #
        #                                                                              #
        ################################################################################
        return ""
    
    def iterative_refinement_with_feedback(self, datapoint: ProgramSynthesisDatapoint) -> str:
        ################################################################################
        #                                                                              #
        # TODO: Part 2c. Implement your iterative refinement prompting method with     #
        # evaluation feedback.                                                         #
        #                                                                              #
        ################################################################################
        return ""

    def YOUR_CUSTOM_PROMPTING_METHOD(self, datapoint: ProgramSynthesisDatapoint) -> str:
        ################################################################################
        #                                                                              #
        # TODO: Part 2d. Implement your custom prompting method.                       #
        #                                                                              #
        # Note: Please change the method name to your custom prompting method.         #
        #                                                                              #
        ################################################################################
        return ""

    def evaluate(self, datapoint: ProgramSynthesisDatapoint, synthesized_program: str) -> EvaluationReport:
        """Evaluate synthesized program (to be implemented by subclasses)."""
        raise NotImplementedError("Evaluate method must be implemented by subclasses")


class MockSynthesizer:
    """Mock synthesizer for dry-run mode that simulates synthesis failures.

    This class provides a MockSynthesizer that can be used during development
    and testing to simulate the synthesis and evaluation pipeline without making
    actual API calls to language models.
    """
    
    def __init__(self, target_language: str, prompting_method: str, model_name: str):
        """
        Initialize the mock synthesizer.
        
        Args:
            target_language: Target programming language (python, rust, ocaml)
            prompting_method: Prompting method to use
            model_name: Name of the model to use
        """
        self.target_language = target_language
        self.prompting_method = prompting_method
        self.model_name = model_name
        
        # Store configuration
        self.config = {
            "target_language": target_language,
            "prompting_method": prompting_method,
            "model_name": model_name
        }
    
    def synthesize(self, datapoint: ProgramSynthesisDatapoint) -> str:
        """
        Simulate synthesis by generating a mock program that will fail.
        
        Args:
            datapoint: The problem datapoint to synthesize a solution for
            
        Returns:
            Mock synthesized program as string
        """
        # Generate a mock program based on target language
        if self.target_language == "python":
            mock_program = self._generate_mock_python_program()
        elif self.target_language == "rust":
            mock_program = self._generate_mock_rust_program()
        elif self.target_language == "ocaml":
            mock_program = self._generate_mock_ocaml_program()
        else:
            mock_program = f"// Mock {self.target_language} program\n// This will fail compilation"
        
        # Simulate some processing time
        time.sleep(random.uniform(0.1, 0.5))
        
        # Simulate LLM response with markdown code blocks
        mock_response = f"""Here's my solution to the problem:

First, I need to analyze the problem requirements:
- The problem asks for a solution in {self.target_language}
- I need to consider the input/output specifications
- I should handle edge cases properly

Let me implement the solution:

```{self.target_language}
{mock_program}
```

This solution should work for the given test cases. The approach is to..."""
        
        # Simulate code extraction
        return self._extract_code_from_response(mock_response)
    
    def _extract_code_from_response(self, response: str) -> str:
        """Simulate code extraction from LLM response."""
        import re
        
        # Look for markdown code blocks with language tags (```lang or ```{lang})
        # Pattern matches: ```python, ```rust, ```ocaml, ```{python}, etc.
        code_pattern = r'```(?:{})?(\w+)?\n(.*?)```'.format(self.target_language)
        matches = re.findall(code_pattern, response, re.DOTALL)
        
        if matches:
            # Take the last (most recent) code block
            extracted_code = matches[-1][1].strip()  # matches[-1] is (lang, code)
            return extracted_code
        else:
            # Try to find any code block with the target language
            fallback_pattern = r'```(\w+)\n(.*?)```'
            fallback_matches = re.findall(fallback_pattern, response, re.DOTALL)
            
            # Look for code blocks that match our target language
            for lang, code in fallback_matches:
                if lang.lower() == self.target_language.lower():
                    extracted_code = code.strip()
                    return extracted_code
            
            # If no code blocks found, return the original response
            return response.strip()
    
    def evaluate(self, datapoint: ProgramSynthesisDatapoint, synthesized_program: str) -> EvaluationReport:
        """
        Simulate evaluation by creating a failed evaluation report.
        
        Args:
            datapoint: The problem datapoint
            synthesized_program: The synthesized program to evaluate
            
        Returns:
            Mock evaluation report with simulated results
        """
        # Simulate some processing time
        time.sleep(random.uniform(0.2, 0.8))
        
        # Create a mock evaluation report that simulates various failure modes
        report = EvaluationReport(synthesized_program)
        
        # Randomly choose failure type
        failure_type = random.choice([
            "synthesis_failure",
            "syntax_error",
            "runtime_error", 
            "timeout_error",
            "partial_success",
        ])

        if failure_type == "synthesis_failure":
            report.synthesized = False
            report.compiles = False
            report.executes = False
            report.add_error("synthesizer", "LLM running out of tokens")
            
        elif failure_type == "syntax_error":
            report.compiles = False
            report.add_error("compiler", "SyntaxError: invalid syntax")
            report.add_error("compiler", "IndentationError: unexpected indent")
            
        elif failure_type == "runtime_error":
            report.compiles = True
            report.executes = False
            report.add_error("runtime", "NameError: name 'undefined_var' is not defined")
            
        elif failure_type == "timeout_error":
            report.compiles = True
            report.executes = True
            # Add test results with timeout
            for i, (test_input, expected_output) in enumerate(zip(datapoint.sample_inputs, datapoint.sample_outputs)):
                if i == 0:
                    report.add_test_result(test_input, expected_output, "", "error", "Execution timed out")
                else:
                    report.add_test_result(test_input, expected_output, "", "error", "Test skipped due to timeout")
                    
        elif failure_type == "partial_success":
            report.compiles = True
            report.executes = True
            # Some tests pass, some fail
            for i, (test_input, expected_output) in enumerate(zip(datapoint.sample_inputs, datapoint.sample_outputs)):
                if i % 2 == 0:
                    # Pass half the tests
                    report.add_test_result(test_input, expected_output, expected_output, "passed")
                else:
                    # Fail the other half
                    report.add_test_result(test_input, expected_output, "wrong_output", "failed")
                    
        else:  # complete_failure
            report.compiles = True
            report.executes = True
            # All tests fail
            for test_input, expected_output in zip(datapoint.sample_inputs, datapoint.sample_outputs):
                report.add_test_result(test_input, expected_output, "completely_wrong", "failed")
        
        report.finalize()
        return report
    
    def _generate_mock_python_program(self) -> str:
        """Generate a mock Python program that will have issues."""
        return '''# Mock Python program - this will have errors
def solve_problem():
    # This function has syntax errors
    x = 
    print(x)
    
    # This will cause runtime errors
    undefined_variable
    
    # This might timeout
    import time
    time.sleep(10)
    
solve_problem()
'''
    
    def _generate_mock_rust_program(self) -> str:
        """Generate a mock Rust program that will have issues."""
        return '''// Mock Rust program - this will have compilation errors
fn main() {
    // Syntax error - missing semicolon
    let x = 42
    
    // Undefined variable
    println!("{}", undefined_var);
    
    // This will cause runtime panic
    let vec = vec![1, 2, 3];
    println!("{}", vec[10]); // Index out of bounds
}
'''
    
    def _generate_mock_ocaml_program(self) -> str:
        """Generate a mock OCaml program that will have issues."""
        return '''(* Mock OCaml program - this will have errors *)
let solve_problem () =
  (* Syntax error - missing semicolon *)
  let x = 42
  
  (* Undefined variable *)
  print_endline undefined_var;
  
  (* This will cause runtime error *)
  let lst = [1; 2; 3] in
  List.nth lst 10 (* Index out of bounds *)

let () = solve_problem ()
'''

