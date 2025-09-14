import os
import tempfile
import subprocess
import time
from typing import Optional
from synthesizer import ProgramSynthesizer
from logger import SynthesisLogger
from report import EvaluationReport
from dataset import ProgramSynthesisDatapoint


class OCamlProgramSynthesizer(ProgramSynthesizer):
    def __init__(self, prompting_method: str = "zero_shot", model_name: str = "gemini-1.5-flash", 
                 api_key: Optional[str] = None, logger: Optional[SynthesisLogger] = None):
        super().__init__("ocaml", prompting_method, model_name, api_key, logger)
        self._ocaml_available = self._check_ocaml_availability()
    
    def _check_ocaml_availability(self) -> bool:
        """Check if OCaml is available and set up environment once."""
        try:
            # Check if ocaml command is available
            result = subprocess.run(
                ["ocaml", "-version"],
                capture_output=True,
                timeout=5,
                text=True
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def evaluate(self, datapoint: ProgramSynthesisDatapoint, synthesized_program: str) -> EvaluationReport:
        """Evaluate OCaml program with comprehensive execution testing."""
        report = EvaluationReport(synthesized_program)
        
        # Create temporary directory for execution
        with tempfile.TemporaryDirectory() as temp_dir:
            ################################################################################
            #                                                                              #
            # TODO: Part 1c. Evaluate OCaml program with comprehensive execution testing.  #
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
    