#!/usr/bin/env python3
"""
Script to synthesize a single program using the specified prompting method and model.

This script loads a dataset from dataset.py and synthesizes a program for a specific
datapoint using the specified model and prompting method.

Usage:
    python synthesize_one.py \
        --model-name gemini-2.5-flash-lite \
        --prompting-method zero_shot \
        --target-language python \
        --datapoint-id c5d19dc8f2478ee8d9cba8cc2e4cd838
"""

import argparse
import sys
import os
from typing import Optional

# Add current directory to path to import local modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dataset import ProgramSynthesisDataset, ProgramSynthesisDatapoint
from synthesizer_python import PythonProgramSynthesizer
from synthesizer_rust import RustProgramSynthesizer
from synthesizer_ocaml import OCamlProgramSynthesizer
from logger import SynthesisLogger


def find_datapoint_by_id(dataset: ProgramSynthesisDataset, datapoint_id: str) -> Optional[ProgramSynthesisDatapoint]:
    """
    Find a datapoint by its src_uid.
    
    Args:
        dataset: The dataset to search in
        datapoint_id: The src_uid to search for
        
    Returns:
        The datapoint if found, None otherwise
    """
    for datapoint in dataset:
        if datapoint.src_uid == datapoint_id:
            return datapoint
    return None


def get_synthesizer(target_language: str, prompting_method: str, model_name: str, 
                   api_key: Optional[str] = None, logger: Optional[SynthesisLogger] = None):
    """
    Get the appropriate synthesizer for the target language.
    
    Args:
        target_language: Target programming language (python, rust, ocaml)
        prompting_method: Prompting method to use
        model_name: Name of the model to use
        api_key: API key for the model (optional)
        logger: Logger instance (optional)
        
    Returns:
        Appropriate synthesizer instance
        
    Raises:
        ValueError: If target_language is not supported
    """
    if target_language == "python":
        return PythonProgramSynthesizer(prompting_method, model_name, api_key, logger)
    elif target_language == "rust":
        return RustProgramSynthesizer(prompting_method, model_name, api_key, logger)
    elif target_language == "ocaml":
        return OCamlProgramSynthesizer(prompting_method, model_name, api_key, logger)
    else:
        raise ValueError(f"Unsupported target language: {target_language}. "
                        f"Supported languages: python, rust, ocaml")


def print_datapoint_info(datapoint: ProgramSynthesisDatapoint):
    """Print information about the datapoint."""
    print(f"\n{'='*60}")
    print(f"DATAPOINT INFORMATION")
    print(f"{'='*60}")
    print(f"ID: {datapoint.src_uid}")
    print(f"Difficulty: {datapoint.difficulty}")
    print(f"Tags: {', '.join(datapoint.tags) if datapoint.tags else 'None'}")
    print(f"\nDescription:")
    print(f"{datapoint.description}")
    print(f"\nInput Specification:")
    print(f"{datapoint.input_spec}")
    print(f"\nOutput Specification:")
    print(f"{datapoint.output_spec}")
    print(f"\nSample Inputs/Outputs:")
    for i, (input_val, output_val) in enumerate(zip(datapoint.sample_inputs, datapoint.sample_outputs)):
        print(f"  {i+1}. Input: {input_val} -> Output: {output_val}")
    print(f"{'='*60}\n")


def print_synthesis_result(synthesized_program: str, evaluation_report=None):
    """Print the synthesis result and evaluation."""
    print(f"\n{'='*60}")
    print(f"SYNTHESIZED PROGRAM")
    print(f"{'='*60}")
    print(synthesized_program)
    print(f"{'='*60}")
    
    if evaluation_report:
        print(f"\n{'='*60}")
        print(f"EVALUATION RESULTS")
        print(f"{'='*60}")
        print(f"Overall Status: {evaluation_report.overall_status}")
        print(f"Success Rate: {evaluation_report.success_rate:.2%}")
        print(f"Compiles: {evaluation_report.compiles}")
        print(f"Executes: {evaluation_report.executes}")
        print(f"Tests Passed: {evaluation_report.passed_tests}/{evaluation_report.total_tests}")
        
        if evaluation_report.compiler_errors:
            print(f"\nCompiler Errors:")
            for error in evaluation_report.compiler_errors:
                print(f"  - {error}")
        
        if evaluation_report.runtime_errors:
            print(f"\nRuntime Errors:")
            for error in evaluation_report.runtime_errors:
                print(f"  - {error}")
        
        if evaluation_report.test_results:
            print(f"\nTest Results:")
            for i, test in enumerate(evaluation_report.test_results, 1):
                status_icon = "✅" if test["status"] == "passed" else "❌" if test["status"] == "failed" else "💥"
                print(f"  {i}. {status_icon} Input: {test['input']}")
                print(f"     Expected: {test['expected_output']}")
                print(f"     Got: {test['actual_output']}")
                if test.get("error"):
                    print(f"     Error: {test['error']}")
        print(f"{'='*60}\n")


def main():
    """Main function to run the synthesis script."""
    parser = argparse.ArgumentParser(
        description="Synthesize a single program using specified prompting method and model",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python synthesize_one.py --model-name gemini-2.5-flash-lite --prompting-method zero_shot --target-language python --datapoint-id c5d19dc8f2478ee8d9cba8cc2e4cd838
  
  python synthesize_one.py --model-name gemini-1.5-flash --prompting-method two_step_chain_of_thought --target-language rust --datapoint-id abc123
  
  python synthesize_one.py --model-name gemini-2.5-flash-lite --prompting-method iterative_refinement --target-language ocaml --datapoint-id def456
        """
    )
    
    parser.add_argument(
        "--model-name",
        required=True,
        choices=["gemini-2.5-flash-lite", "gemini-1.5-flash"],
        help="Name of the Gemini model to use"
    )
    
    parser.add_argument(
        "--prompting-method",
        required=True,
        help="Prompting method to use (e.g., zero_shot, two_step_chain_of_thought, iterative_refinement, etc.)"
    )
    
    parser.add_argument(
        "--target-language",
        required=True,
        choices=["python", "rust", "ocaml"],
        help="Target programming language"
    )
    
    parser.add_argument(
        "--datapoint-id",
        required=True,
        help="src_uid of the datapoint to synthesize (from dataset.jsonl)"
    )
    
    parser.add_argument(
        "--data-file",
        default="data/dataset.jsonl",
        help="Path to the dataset file (default: data/dataset.jsonl)"
    )
    
    parser.add_argument(
        "--api-key",
        help="API key for the model (if not provided, will use GEMINI_API_KEY environment variable)"
    )
    
    parser.add_argument(
        "--log-file",
        help="Path to log file for synthesis operations"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    try:
        # Load dataset
        print(f"Loading dataset from {args.data_file}...")
        dataset = ProgramSynthesisDataset(data_file=args.data_file)
        print(f"Loaded {len(dataset)} datapoints")
        
        # Find the specific datapoint
        print(f"Looking for datapoint with ID: {args.datapoint_id}")
        datapoint = find_datapoint_by_id(dataset, args.datapoint_id)
        
        if datapoint is None:
            print(f"Error: Datapoint with ID '{args.datapoint_id}' not found in dataset")
            print(f"Available datapoint IDs:")
            for i, dp in enumerate(dataset):
                if i < 10:  # Show first 10 IDs
                    print(f"  - {dp.src_uid}")
                elif i == 10:
                    print(f"  ... and {len(dataset) - 10} more")
                    break
            sys.exit(1)
        
        # Print datapoint information
        print_datapoint_info(datapoint)
        
        # Setup logger
        logger = SynthesisLogger(args.log_file) if args.log_file else None
        
        # Get synthesizer
        print(f"Initializing {args.target_language} synthesizer with {args.prompting_method} method...")
        synthesizer = get_synthesizer(
            target_language=args.target_language,
            prompting_method=args.prompting_method,
            model_name=args.model_name,
            api_key=args.api_key,
            logger=logger
        )
        
        # Synthesize program
        print(f"Synthesizing program using {args.model_name}...")
        try:
            synthesized_program = synthesizer.synthesize(datapoint)
            print("Synthesis completed successfully!")
            
            # Evaluate the synthesized program
            print("Evaluating synthesized program...")
            evaluation_report = synthesizer.evaluate(datapoint, synthesized_program)
            print("Evaluation completed!")
            
            # Print results
            print_synthesis_result(synthesized_program, evaluation_report)
            
            # Print summary
            print(f"\nSUMMARY:")
            print(f"  Model: {args.model_name}")
            print(f"  Method: {args.prompting_method}")
            print(f"  Language: {args.target_language}")
            print(f"  Datapoint: {args.datapoint_id}")
            print(f"  Success: {evaluation_report.overall_status == 'success'}")
            print(f"  Success Rate: {evaluation_report.success_rate:.2%}")
            
        except Exception as e:
            print(f"Error during synthesis: {str(e)}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
