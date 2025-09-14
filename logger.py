"""
Logging functionality for program synthesis.
"""

import json
import logging
import time
from typing import Dict, Any, Optional


class SynthesisLogger:
    """Logger for synthesis operations."""
    
    def __init__(self, log_file: Optional[str] = None):
        """
        Initialize synthesis logger.
        
        Args:
            log_file: Path to log file (optional). If None, no file logging will be performed.
        """
        self.log_file = log_file
        self.logger = logging.getLogger('synthesis')
        self.logger.setLevel(logging.INFO)
        
        # Create file handler if log_file is provided and no handlers exist
        if log_file and not self.logger.handlers:
            handler = logging.FileHandler(log_file)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log_synthesis(self, datapoint, synthesizer_config: Dict[str, Any], 
                     synthesized_program: str,
                     success: bool = True,
                     error: Optional[str] = None):
        """
        Log a synthesis operation.
        
        Args:
            datapoint: The input datapoint
            synthesizer_config: Configuration of the synthesizer
            synthesized_program: The generated program
            success: Whether synthesis was successful
            error: Error message if synthesis failed
        """
        log_entry = {
            "timestamp": str(time.time()),
            "datapoint": {
                "src_uid": datapoint.src_uid,
                "difficulty": datapoint.difficulty,
                "tags": datapoint.tags,
                "description": datapoint.description[:200] + "..." if len(datapoint.description) > 200 else datapoint.description
            },
            "synthesizer_config": synthesizer_config,
            "synthesized_program": synthesized_program,
            "success": success,
            "error": error
        }
        
        # Log to JSONL file only if log_file is provided
        if self.log_file:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        
        # Log to standard logger
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"Synthesis {status} for datapoint {datapoint.src_uid}")
