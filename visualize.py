#!/usr/bin/env python3
"""
Visualization script for program synthesis evaluation results.

This script generates a main figure with 3 subfigures showing pass@3 metrics
across programming languages, language models, and prompting methods.
"""

import json
import os
import glob
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from typing import Dict, Optional
import argparse


class ExperimentVisualizer:
    """Visualizer for program synthesis experiment results."""
    
    def __init__(self, reports_dir: str = "reports"):
        """
        Initialize the visualizer.
        
        Args:
            reports_dir: Directory containing JSON report files
        """
        self.reports_dir = reports_dir
        
        # Define experiment parameters
        self.languages = ["python", "rust", "ocaml"]
        self.models = ["gemini-2.5-flash-lite", "gemini-1.5-flash"]
        self.prompting_methods = ["zero_shot", "two_step_chain_of_thought", "iterative_refinement", "YOUR_CUSTOM_PROMPTING_METHOD"]
        self.prompting_labels = ["Zero-Shot", "Chain of Thought", "Iterative Refinement", "Your Custom Prompting Method"]

        ################################################################################
        #                                                                              #
        # TODO: Part 4b. Specify your own prompting method above.                      #
        #                                                                              #
        ################################################################################
        
        # Colors for prompting methods
        self.colors = {
            "zero_shot": "#1f77b4",
            "two_step_chain_of_thought": "#ff7f0e", 
            "iterative_refinement": "#2ca02c",
            "YOUR_CUSTOM_PROMPTING_METHOD": "#d62728"
        }
        
        # Load all experiment results
        self.experiment_data = self._load_experiment_data()
    
    def _load_experiment_data(self) -> Dict[str, Dict[str, Dict[str, float]]]:
        """
        Load experiment results from JSON report files.
        
        Returns:
            Nested dictionary: language -> model -> prompting_method -> pass@3 value
        """
        experiment_data = {}
        
        # Initialize structure
        for language in self.languages:
            experiment_data[language] = {}
            for model in self.models:
                experiment_data[language][model] = {}
                for method in self.prompting_methods:
                    experiment_data[language][model][method] = 0.0
        
        # Load data from report files
        report_files = glob.glob(os.path.join(self.reports_dir, "final_report_*.json"))
        
        for report_file in report_files:
            try:
                with open(report_file, 'r') as f:
                    data = json.load(f)
                
                # Extract experiment parameters from filename or data
                config = data.get("experiment_config", {})
                language = config.get("target_language")
                model = config.get("model_name")
                method = config.get("prompting_method")
                
                # Get pass@3 metric
                pass_at_k_metrics = data.get("pass_at_k_metrics", {})
                pass_at_3 = pass_at_k_metrics.get("pass@3", 0.0)
                
                # Store in data structure
                if (language in self.languages and 
                    model in self.models and 
                    method in self.prompting_methods):
                    experiment_data[language][model][method] = pass_at_3
                    print(f"Loaded: {language}, {model}, {method} -> pass@3: {pass_at_3:.3f}")
                
            except Exception as e:
                print(f"Error loading {report_file}: {e}")
                continue
        
        return experiment_data
    
    def plot_main_figure(self, save_path: Optional[str] = None, use_mock_data: bool = False):
        """
        Create the main figure with 3 subfigures for each programming language.
        
        Args:
            save_path: Path to save the figure (optional, defaults to visualizations/main_figure.png)
            use_mock_data: Whether to use mock data instead of real data
        """
        # Set default save path to visualizations directory
        if save_path is None:
            save_path = "visualizations/main_figure.png"

        # Use mock data if requested or no real data available
        data_to_plot = self.experiment_data

        # Create figure with 3 subplots
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        fig.suptitle('Pass@3 Metrics Across Programming Languages, Models, and Prompting Methods', 
                     fontsize=16, fontweight='bold')
        
        # Plot each language
        for i, language in enumerate(self.languages):
            ax = axes[i]
            self._plot_language_subplot(ax, language, data_to_plot[language])
        
        # Add legend
        legend_elements = [
            mpatches.Patch(color=self.colors[method], label=label)
            for method, label in zip(self.prompting_methods, self.prompting_labels)
        ]
        fig.legend(handles=legend_elements, loc='upper center', 
                  bbox_to_anchor=(0.5, 0.02), ncol=3, fontsize=12)
        
        # Adjust layout
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.15)
        
        # Save or show
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Figure saved to: {save_path}")
    
    def _plot_language_subplot(self, ax, language: str, language_data: Dict[str, Dict[str, float]]):
        """
        Plot a subplot for a specific programming language.
        
        Args:
            ax: Matplotlib axis object
            language: Programming language name
            language_data: Data for this language
        """
        # Set up data for grouped bar chart
        x = np.arange(len(self.models))  # Model positions
        width = 0.25  # Width of bars
        
        # Plot bars for each prompting method
        for i, (method, label) in enumerate(zip(self.prompting_methods, self.prompting_labels)):
            values = [language_data[model][method] for model in self.models]
            bars = ax.bar(x + i * width, values, width, 
                         label=label, color=self.colors[method], 
                         alpha=0.8, edgecolor='black', linewidth=0.5)
            
            # Add value labels on bars
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                       f'{value:.3f}', ha='center', va='bottom', fontsize=9)
        
        # Customize subplot
        ax.set_title(f'{language.capitalize()}', fontsize=14, fontweight='bold')
        ax.set_xlabel('Language Model', fontsize=12)
        ax.set_ylabel('Pass@3', fontsize=12)
        ax.set_xticks(x + width)
        ax.set_xticklabels(self.models, fontsize=10)
        ax.set_ylim(0, 1.0)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add horizontal line at 50%
        ax.axhline(y=0.5, color='red', linestyle='--', alpha=0.5, linewidth=1)
    
    def PLOT_YOUR_CUSTOM_FIGURE(self, save_path: Optional[str] = None):
        ################################################################################
        #                                                                              #
        # TODO: Part 4b. Create a visualization studying one aspect of the synthesis   #
        # experiments.                                                                 #
        #                                                                              #
        # Ideas:                                                                       #
        # - Plot a line chart of pass@x for x=1, 2, 3                                  #
        # - Plot a pie chart of distribution of errors (syntax, compile, runtime)      #
        # - Plot a violin plot of execution time by language                           #
        # - Plot a line chart of accuracy over number of refinement steps              #
        #                                                                              #
        ################################################################################
        pass

    def print_data_summary(self):
        """Print a summary of the loaded experiment data."""
        print("\n" + "="*60)
        print("EXPERIMENT DATA SUMMARY")
        print("="*60)
        
        for language in self.languages:
            print(f"\n{language.upper()}:")
            for model in self.models:
                print(f"  {model}:")
                for method in self.prompting_methods:
                    value = self.experiment_data[language][model][method]
                    print(f"    {method}: {value:.3f}")
        
        # Check for missing data
        missing_experiments = []
        for language in self.languages:
            for model in self.models:
                for method in self.prompting_methods:
                    if self.experiment_data[language][model][method] == 0.0:
                        missing_experiments.append(f"{language}-{model}-{method}")
        
        if missing_experiments:
            print(f"\nMissing experiments ({len(missing_experiments)}):")
            for exp in missing_experiments:
                print(f"  - {exp}")
        else:
            print("\nAll experiments completed!")


def main():
    """Main entry point for the visualization script."""
    parser = argparse.ArgumentParser(description="Visualize program synthesis experiment results")
    parser.add_argument("--reports-dir", "-d", default="reports", help="Directory containing JSON report files (default: reports)")
    parser.add_argument("--save-path", "-s", help="Path to save the figure (default: visualizations/main_figure.png)")
    parser.add_argument("--summary-only", action="store_true", help="Print data summary only, don't create plots")
    
    args = parser.parse_args()
    
    # Create visualizer
    visualizer = ExperimentVisualizer(args.reports_dir)
    
    # Print data summary
    visualizer.print_data_summary()
    
    if not args.summary_only:
        # Create visualizations directory if it doesn't exist
        os.makedirs("visualizations", exist_ok=True)
        
        # Create and display the main figure
        visualizer.plot_main_figure(save_path=args.save_path, use_mock_data=args.mock_data)

        ################################################################################
        #                                                                              #
        # TODO: Part 4b. Your own visualization plot. Uncomment the line below.        #
        #                                                                              #
        ################################################################################
        
        # visualizer.PLOT_YOUR_CUSTOM_FIGURE(save_path=args.save_path)


if __name__ == "__main__":
    main()
