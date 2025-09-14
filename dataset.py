
import json
import os
from typing import List, Optional, Dict, Any


class ProgramSynthesisDatapoint:
    def __init__(self, data: Dict[str, Any]):
        """
        Initialize a program synthesis datapoint from a dictionary.
        
        Args:
            data: Dictionary containing problem data from JSONL file
        """
        self.description = data.get("description", "")
        self.input_from = data.get("input_from", "")
        self.output_to = data.get("output_to", "")
        self.time_limit = data.get("time_limit", 5.0)  # Default to 5.0 seconds
        self.memory_limit = data.get("memory_limit", "")
        self.input_spec = data.get("input_spec", "")
        self.output_spec = data.get("output_spec", "")
        self.notes = data.get("notes", "")
        self.sample_inputs = data.get("sample_inputs", [])
        self.sample_outputs = data.get("sample_outputs", [])
        self.tags = data.get("tags", [])
        self.src_uid = data.get("src_uid", "")
        self.difficulty = data.get("difficulty")
    
    def __str__(self):
        return f"ProgramSynthesisDatapoint(difficulty={self.difficulty}, tags={self.tags})"
    
    def __repr__(self):
        return self.__str__()


class ProgramSynthesisDataset:
    def __init__(self, 
                 data_file: str = "data/prog_syn_val.jsonl",
                 difficulty_cutoff: Optional[int] = None,
                 max_samples: int = 20):
        """
        Initialize a program synthesis dataset.
        
        Args:
            data_file: Path to the JSONL data file (relative to this file)
            difficulty_cutoff: Maximum difficulty level to include (None for no filter)
            max_samples: Maximum number of samples to load (default: 20)
        """
        self.data_file = data_file
        self.difficulty_cutoff = difficulty_cutoff
        self.max_samples = max_samples
        self.datapoints: List[ProgramSynthesisDatapoint] = []
        
        self._load_data()
    
    def _load_data(self):
        """Load data from the JSONL file with filtering."""
        # Get the directory of the current file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, self.data_file)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Data file not found: {file_path}")
        
        loaded_samples = 0
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if loaded_samples >= self.max_samples:
                    break
                    
                line = line.strip()
                if not line:
                    continue
                
                try:
                    data = json.loads(line)
                    
                    # Apply difficulty filter if specified
                    if self.difficulty_cutoff is not None:
                        difficulty = data.get("difficulty")
                        if difficulty is None or difficulty > self.difficulty_cutoff:
                            continue
                    
                    datapoint = ProgramSynthesisDatapoint(data)
                    self.datapoints.append(datapoint)
                    loaded_samples += 1
                    
                except json.JSONDecodeError as e:
                    print(f"Warning: Skipping invalid JSON line: {e}")
                    continue
    
    def __len__(self):
        return len(self.datapoints)
    
    def __getitem__(self, idx):
        return self.datapoints[idx]
    
    def __iter__(self):
        return iter(self.datapoints)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the loaded dataset."""
        if not self.datapoints:
            return {"total_samples": 0}
        
        difficulties = [dp.difficulty for dp in self.datapoints if dp.difficulty is not None]
        all_tags = []
        for dp in self.datapoints:
            all_tags.extend(dp.tags)
        
        stats = {
            "total_samples": len(self.datapoints),
            "difficulty_range": (min(difficulties), max(difficulties)) if difficulties else None,
            "avg_difficulty": sum(difficulties) / len(difficulties) if difficulties else None,
            "unique_tags": len(set(all_tags)),
            "most_common_tags": self._get_most_common_tags(all_tags)
        }
        
        return stats
    
    def _get_most_common_tags(self, all_tags: List[str], top_k: int = 5) -> List[tuple]:
        """Get the most common tags in the dataset."""
        from collections import Counter
        tag_counts = Counter(all_tags)
        return tag_counts.most_common(top_k)
    
    def filter_by_tags(self, tags: List[str]) -> 'ProgramSynthesisDataset':
        """Create a new dataset filtered by tags."""
        filtered_datapoints = []
        for dp in self.datapoints:
            if any(tag in dp.tags for tag in tags):
                filtered_datapoints.append(dp)
        
        new_dataset = ProgramSynthesisDataset.__new__(ProgramSynthesisDataset)
        new_dataset.data_file = self.data_file
        new_dataset.difficulty_cutoff = self.difficulty_cutoff
        new_dataset.max_samples = self.max_samples
        new_dataset.datapoints = filtered_datapoints
        return new_dataset