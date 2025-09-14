#!/usr/bin/env python3
"""
Evaluation script for program synthesis.

Usage:
    python evaluate.py --target-language python --prompting-method zero_shot --model-name gemini-1.5-flash --max-pass-at-k 5 --samples 10
    python evaluate.py --target-language python --prompting-method zero_shot --dry-run --max-pass-at-k 3 --samples 5
"""

import argparse
import os
import sys
import time
from typing import Dict, Any, List, Optional
from collections import defaultdict

from dataset import ProgramSynthesisDataset
from logger import SynthesisLogger
from report import EvaluationReport
from synthesizer import MockSynthesizer


class Evaluator:
    """
    Main evaluator class for program synthesis experiments.
    """
    
    def __init__(self, target_language: str, prompting_method: str, model_name: str, 
                 api_key: Optional[str] = None, max_pass_at_k: int = 5, samples: int = 30,
                 dry_run: bool = False, api_timeout: int = 120):
        """
        Initialize the evaluator.
        
        Args:
            target_language: Target programming language (python, rust, ocaml)
            prompting_method: Prompting method to use
            model_name: Name of the model to use
            api_key: API key for the model (optional, will use environment variable)
            max_pass_at_k: Maximum number of attempts for pass@k calculation
            samples: Number of samples to evaluate
            dry_run: If True, simulate synthesis without making API calls
            api_timeout: API timeout in seconds
        """
        self.target_language = target_language
        self.prompting_method = prompting_method
        self.model_name = model_name
        self.api_key = api_key
        self.max_pass_at_k = max_pass_at_k
        self.samples = samples
        self.dry_run = dry_run
        self.api_timeout = api_timeout
        
        # Initialize synthesizer based on target language
        if dry_run:
            self.synthesizer = self._initialize_mock_synthesizer()
        else:
            self.synthesizer = self._initialize_synthesizer()
        
        # Initialize dataset
        self.dataset = ProgramSynthesisDataset(max_samples=samples)

        # Initialize logger with detailed filename
        log_filename = f"reports/{target_language}_{prompting_method}_{model_name}.jsonl"
        self.logger = SynthesisLogger(log_filename)
        
        # Student-implemented results storage
        self.datapoint_logs: List[Dict[str, Any]] = []
        
    def _initialize_synthesizer(self):
        """Initialize the appropriate synthesizer based on target language."""
        try:
            if self.target_language == "python":
                from synthesizer_python import PythonProgramSynthesizer
                synthesizer = PythonProgramSynthesizer(
                    self.prompting_method, self.model_name, self.api_key, None
                )
            elif self.target_language == "rust":
                from synthesizer_rust import RustProgramSynthesizer
                synthesizer = RustProgramSynthesizer(
                    self.prompting_method, self.model_name, self.api_key, None
                )
            elif self.target_language == "ocaml":
                from synthesizer_ocaml import OCamlProgramSynthesizer
                synthesizer = OCamlProgramSynthesizer(
                    self.prompting_method, self.model_name, self.api_key, None
                )
            else:
                raise ValueError(f"Unsupported target language: {self.target_language}")
            
            # Set the API timeout
            synthesizer.model.api_timeout = self.api_timeout
            return synthesizer
            
        except ImportError as e:
            raise ImportError(f"Failed to import synthesizer for {self.target_language}: {e}")
    
    def _initialize_mock_synthesizer(self):
        """Initialize a mock synthesizer for dry-run mode."""
        return MockSynthesizer(self.target_language, self.prompting_method, self.model_name)
    
    def run_evaluation(self) -> Dict[str, Any]:
        """
        Run the complete evaluation process.
        
        This method orchestrates the evaluation but delegates the core logic
        to student-implemented methods.
        
        Returns:
            Dictionary containing comprehensive evaluation results
        """
        print(f"\nStarting evaluation with {len(self.dataset)} datapoints...")
        print(f"Running {self.max_pass_at_k} attempts per datapoint for pass@k calculation\n")
        
        start_time = time.time()
        
        # Main evaluation loop - students implement this logic
        self._evaluate_all_datapoints()
        
        total_time = time.time() - start_time
        
        # Generate final report from student results
        final_report = self._generate_final_report(total_time)
        
        print("Evaluation completed!")
        print(f"Total time: {total_time:.2f}s")
        print(f"Average time per datapoint: {total_time/len(self.dataset):.2f}s")
        
        return final_report
    
    def _evaluate_all_datapoints(self):
        ################################################################################
        #                                                                              #
        # TODO: Part 3a. Implement the main evaluation loop.                           #
        #                                                                              #
        # Populate the self.datapoint_logs with the evaluation results.                #
        #                                                                              #
        # Structure for datapoint_logs:                                                #
        # [                                                                            #
        #     {                                                                        #
        #         "src_uid": "c9e79e83928d5d034123ebc3b2f5e064",                       #
        #         "difficulty": 2600,                                                  #
        #         "tags": ["array", "sorting"],                                        #
        #         "attempts": [                                                        #
        #             {                                                                #
        #                 "attempt_number": 1,                                         #
        #                 "synthesized_program": "...",                                #
        #                 "evaluation_report": {...},                                  #
        #                 "success": True/False,                                       #
        #                 "synthesis_time": 1.5,                                       #
        #                 "evaluation_time": 0.8                                       #
        #             },                                                               #
        #             ...                                                              #
        #         ],                                                                   #
        #         "passed_at_k": 2,  # None if never passed                            #
        #         "best_success_rate": 0.8                                             #
        #     },                                                                       #
        #     ...                                                                      #
        # ]                                                                            #
        #                                                                              #
        ################################################################################
        pass
    
    def _save_detailed_logs(self):
        """
        INFRASTRUCTURE: Save detailed logs to file
        
        This method handles the complex logging infrastructure that students
        don't need to worry about. It converts the student's simple datapoint_logs
        into detailed JSONL format for analysis.
        """
        import json
        
        if not self.logger.log_file:
            return
            
        with open(self.logger.log_file, 'w', encoding='utf-8') as f:
            for datapoint_log in self.datapoint_logs:
                for attempt in datapoint_log["attempts"]:
                    log_entry = {
                        "timestamp": time.time(),
                        "datapoint": {
                            "src_uid": datapoint_log["src_uid"],
                            "difficulty": datapoint_log["difficulty"],
                            "tags": datapoint_log["tags"]
                        },
                        "attempt": {
                            "number": attempt["attempt_number"],
                            "max_attempts": self.max_pass_at_k
                        },
                        "synthesizer_config": {
                            "target_language": self.target_language,
                            "prompting_method": self.prompting_method,
                            "model_name": self.model_name
                        },
                        "synthesized_program": attempt["synthesized_program"],
                        "evaluation_report": attempt["evaluation_report"],
                        "timing": {
                            "synthesis_time": attempt["synthesis_time"],
                            "evaluation_time": attempt["evaluation_time"],
                            "total_time": attempt["synthesis_time"] + attempt["evaluation_time"]
                        },
                        "success": attempt["success"],
                        "error": attempt.get("error")
                    }
                    f.write(json.dumps(log_entry) + '\n')
    
    def _generate_final_report(self, total_time: float) -> Dict[str, Any]:
        """
        INFRASTRUCTURE: Generate comprehensive final evaluation report
        
        This method processes the student's simple datapoint_logs and generates
        a comprehensive report with pass@k metrics and statistics.
        """
        # Save detailed logs first
        self._save_detailed_logs()
        
        # Calculate pass@k metrics from student results
        pass_at_k_metrics = self._compute_pass_at_k_metrics()
        
        # Calculate timing statistics from student results
        timing_stats = self._compute_timing_statistics()
        
        # Calculate success rates from student results
        success_rates = self._compute_success_rates()
        
        # Calculate summary statistics
        total_datapoints = len(self.datapoint_logs)
        total_attempts = sum(len(log["attempts"]) for log in self.datapoint_logs)
        
        final_report = {
            "experiment_config": {
                "target_language": self.target_language,
                "prompting_method": self.prompting_method,
                "model_name": self.model_name,
                "max_pass_at_k": self.max_pass_at_k,
                "samples": self.samples,
                "log_file": self.logger.log_file
            },
            "summary_statistics": {
                "total_datapoints": total_datapoints,
                "total_attempts": total_attempts,
                "successful_syntheses": success_rates["successful_attempts"],
                "overall_success_rate": success_rates["overall_success_rate"],
                "datapoint_success_rate": success_rates["datapoint_success_rate"],
                "total_evaluation_time": total_time,
                "average_time_per_datapoint": total_time / total_datapoints if total_datapoints > 0 else 0
            },
            "pass_at_k_metrics": pass_at_k_metrics,
            "timing_statistics": timing_stats,
            "detailed_results": self.datapoint_logs
        }
        
        return final_report
    
    def _compute_pass_at_k_metrics(self) -> Dict[str, float]:
        ################################################################################
        #                                                                              #
        # TODO: Part 3b. Compute pass@k metrics from self.datapoint_logs.              #
        #                                                                              #
        # Populate the pass@k metrics in the return dictionary.                        #
        #                                                                              #
        # Structure for pass@k metrics, given that max_pass_at_k is 3:                 #
        # {                                                                            #
        #     "pass@1": 0.5,                                                           #
        #     "pass@2": 0.7,                                                           #
        #     "pass@3": 0.8,                                                           #
        # }                                                                            #
        #                                                                              #
        ################################################################################
        pass
    
    def _compute_timing_statistics(self) -> Dict[str, float]:
        """
        INFRASTRUCTURE: Compute timing statistics from student results
        """
        all_synthesis_times = []
        all_evaluation_times = []
        
        for datapoint_log in self.datapoint_logs:
            for attempt in datapoint_log["attempts"]:
                all_synthesis_times.append(attempt["synthesis_time"])
                all_evaluation_times.append(attempt["evaluation_time"])
        
        return {
            "average_synthesis_time": sum(all_synthesis_times) / len(all_synthesis_times) if all_synthesis_times else 0,
            "average_evaluation_time": sum(all_evaluation_times) / len(all_evaluation_times) if all_evaluation_times else 0,
            "total_synthesis_time": sum(all_synthesis_times),
            "total_evaluation_time": sum(all_evaluation_times)
        }
    
    def _compute_success_rates(self) -> Dict[str, float]:
        """
        INFRASTRUCTURE: Compute success rates from student results
        """
        total_attempts = 0
        successful_attempts = 0
        datapoints_with_success = 0
        
        for datapoint_log in self.datapoint_logs:
            if datapoint_log.get("passed_at_k") is not None:
                datapoints_with_success += 1
            
            for attempt in datapoint_log["attempts"]:
                total_attempts += 1
                if attempt["success"]:
                    successful_attempts += 1
        
        total_datapoints = len(self.datapoint_logs)
        
        return {
            "successful_attempts": successful_attempts,
            "overall_success_rate": successful_attempts / total_attempts if total_attempts > 0 else 0,
            "datapoint_success_rate": datapoints_with_success / total_datapoints if total_datapoints > 0 else 0
        }


def main():
    """Main entry point for the evaluation script."""
    parser = argparse.ArgumentParser(description="Evaluate program synthesis with pass@k metrics", formatter_class=argparse.RawDescriptionHelpFormatter)
    
    parser.add_argument("--target-language", "-l", required=True, choices=["python", "rust", "ocaml"], help="Target programming language")
    parser.add_argument("--prompting-method", "-p", required=True, choices=["zero_shot", "few_shot", "two_step_chain_of_thought", "two_step_self_reflection", "code_transpilation", "iterative_refinement"], help="Prompting method to use")
    parser.add_argument("--model-name", "-m", default="gemini-1.5-flash", help="Name of the model to use (default: gemini-1.5-flash)")
    parser.add_argument("--api-key", help="API key for the model (if not provided, will use GEMINI_API_KEY environment variable)")
    parser.add_argument("--max-pass-at-k", "-k", type=int, default=5, help="Maximum number of attempts for pass@k calculation (default: 5)")
    parser.add_argument("--samples", "-s", type=int, default=30, help="Number of samples to evaluate (default: 30)")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode (no API calls, simulate synthesis failures)")
    parser.add_argument("--api-timeout", type=int, default=120, help="API timeout in seconds (default: 120)")
    
    args = parser.parse_args()
    
    try:
        # Initialize evaluator
        evaluator = Evaluator(
            target_language=args.target_language,
            prompting_method=args.prompting_method,
            model_name=args.model_name,
            api_key=args.api_key,
            max_pass_at_k=args.max_pass_at_k,
            samples=args.samples,
            dry_run=args.dry_run,
            api_timeout=args.api_timeout
        )
        
        # Run evaluation
        final_report = evaluator.run_evaluation()
        
        # Save final report
        report_filename = f"reports/final_report_{args.target_language}_{args.prompting_method}_{args.model_name}.json"
        
        import json
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(final_report, f, indent=2, ensure_ascii=False)
        
        print(f"\nFinal report saved to: {report_filename}")
        
        # Print summary
        print("\n" + "="*60)
        print("EVALUATION SUMMARY")
        print("="*60)
        print(f"Target Language: {args.target_language}")
        print(f"Prompting Method: {args.prompting_method}")
        print(f"Model: {args.model_name}")
        print(f"Total Datapoints: {final_report['summary_statistics']['total_datapoints']}")
        print(f"Total Attempts: {final_report['summary_statistics']['total_attempts']}")
        print(f"Successful Syntheses: {final_report['summary_statistics']['successful_syntheses']}")
        print(f"Overall Success Rate: {final_report['summary_statistics']['overall_success_rate']:.2%}")
        print(f"Datapoint Success Rate: {final_report['summary_statistics']['datapoint_success_rate']:.2%}")
        print(f"Total Time: {final_report['summary_statistics']['total_evaluation_time']:.2f}s")
        print("\nPass@k Metrics:")
        for k, rate in final_report['pass_at_k_metrics'].items():
            print(f"  {k}: {rate:.2%}")
        
        print(f"\nDetailed logs: {evaluator.logger.log_file}")
        print(f"Final report: {report_filename}")
        
    except KeyboardInterrupt:
        print("\nEvaluation interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error during evaluation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
