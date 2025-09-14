import os
import tempfile
import subprocess
import time
import signal
from typing import Optional
from synthesizer import ProgramSynthesizer
from logger import SynthesisLogger
from report import EvaluationReport
from dataset import ProgramSynthesisDatapoint


class RustProgramSynthesizer(ProgramSynthesizer):
    def __init__(self, prompting_method: str = "zero_shot", model_name: str = "gemini-1.5-flash", 
                 api_key: Optional[str] = None, logger: Optional[SynthesisLogger] = None):
        super().__init__("rust", prompting_method, model_name, api_key, logger)

    def evaluate(self, datapoint: ProgramSynthesisDatapoint, synthesized_program: str) -> EvaluationReport:
        """Evaluate Rust program with comprehensive compilation and execution testing."""
        report = EvaluationReport(synthesized_program)
        
        # Create temporary directory for compilation
        with tempfile.TemporaryDirectory() as temp_dir:
            ################################################################################
            #                                                                              #
            # TODO: Part 1b. Evaluate Rust program with comprehensive execution testing.   #
            #                                                                              #
            # Populate the report with the evaluation results. Check for syntax errors,    #
            # runtime errors, and test cases (which are in datapoint.sample_inputs and     #
            # datapoint.sample_outputs).                                                   #
            #                                                                              #
            # To run the program, you can create a temporary file and write the program to #
            # it. Then, you can use subprocess to run the program with the test cases.     #
            #                                                                              #
            ################################################################################
            pass
        
        report.finalize()
        return report
