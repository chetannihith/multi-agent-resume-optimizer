"""
Workflow Visualization Module for Multi-Agent Resume Optimizer.

This module provides comprehensive visualization capabilities for the resume
optimization workflow, including flowcharts, agent interactions, performance
metrics, and execution timelines using various plotting libraries.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from pathlib import Path

# Visualization libraries
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.patches import FancyBboxPatch, ConnectionPatch
    import seaborn as sns
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import networkx as nx
    from networkx.drawing.nx_agraph import graphviz_layout
except ImportError as e:
    print(f"Warning: Some visualization dependencies not available: {e}")
    print("Install with: pip install matplotlib seaborn plotly networkx pygraphviz")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AgentNode:
    """Data class representing an agent in the workflow."""
    name: str
    step: int
    status: str = "pending"  # pending, in_progress, completed, failed
    execution_time: float = 0.0
    inputs: List[str] = None
    outputs: List[str] = None
    dependencies: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.inputs is None:
            self.inputs = []
        if self.outputs is None:
            self.outputs = []
        if self.dependencies is None:
            self.dependencies = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class WorkflowMetrics:
    """Data class for workflow performance metrics."""
    total_execution_time: float
    step_times: Dict[str, float]
    success_rate: float
    error_count: int
    warning_count: int
    ats_score: Optional[float] = None
    alignment_score: Optional[float] = None
    keyword_match_percentage: Optional[float] = None


class WorkflowVisualizer:
    """
    Comprehensive workflow visualization system for the multi-agent resume optimizer.
    
    This class provides various plotting capabilities including:
    - Workflow flowcharts
    - Agent interaction diagrams
    - Performance metrics visualization
    - Execution timelines
    - ATS score analysis
    - Keyword alignment charts
    """
    
    def __init__(
        self,
        output_directory: str = "output/visualizations",
        style: str = "professional",
        color_scheme: str = "default"
    ):
        """
        Initialize the WorkflowVisualizer.
        
        Args:
            output_directory: Directory to save visualization files
            style: Visualization style ('professional', 'modern', 'minimal')
            color_scheme: Color scheme ('default', 'blue', 'green', 'purple')
        """
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(parents=True, exist_ok=True)
        
        # Set visualization style
        self._setup_style(style, color_scheme)
        
        # Define agent information
        self.agents = {
            "JDExtractorAgent": {
                "description": "Extract job requirements",
                "color": self.colors["primary"],
                "icon": "🔍"
            },
            "ProfileRAGAgent": {
                "description": "Retrieve profile data",
                "color": self.colors["secondary"],
                "icon": "📚"
            },
            "ContentAlignmentAgent": {
                "description": "Align content with JD",
                "color": self.colors["accent"],
                "icon": "🎯"
            },
            "ATSOptimizerAgent": {
                "description": "Optimize for ATS",
                "color": self.colors["success"],
                "icon": "⚡"
            },
            "LaTeXFormatterAgent": {
                "description": "Generate LaTeX resume",
                "color": self.colors["warning"],
                "icon": "📄"
            }
        }
        
        logger.info(f"WorkflowVisualizer initialized with style: {style}")
    
    def _setup_style(self, style: str, color_scheme: str) -> None:
        """Setup visualization style and colors."""
        # Color schemes
        color_schemes = {
            "default": {
                "primary": "#2E86AB",
                "secondary": "#A23B72", 
                "accent": "#F18F01",
                "success": "#C73E1D",
                "warning": "#7209B7",
                "background": "#F8F9FA",
                "text": "#212529"
            },
            "blue": {
                "primary": "#1E3A8A",
                "secondary": "#3B82F6",
                "accent": "#60A5FA",
                "success": "#10B981",
                "warning": "#F59E0B",
                "background": "#F0F9FF",
                "text": "#1E293B"
            },
            "green": {
                "primary": "#166534",
                "secondary": "#22C55E",
                "accent": "#84CC16",
                "success": "#059669",
                "warning": "#D97706",
                "background": "#F0FDF4",
                "text": "#14532D"
            }
        }
        
        self.colors = color_schemes.get(color_scheme, color_schemes["default"])
        
        # Set matplotlib style
        if style == "professional":
            plt.style.use('default')
            sns.set_palette([self.colors["primary"], self.colors["secondary"], 
                           self.colors["accent"], self.colors["success"]])
        elif style == "modern":
            plt.style.use('seaborn-v0_8')
        else:  # minimal
            plt.style.use('default')
    
    def create_workflow_flowchart(
        self,
        workflow_data: Dict[str, Any],
        show_execution_times: bool = True,
        show_status: bool = True,
        format: str = "png"
    ) -> str:
        """
        Create a comprehensive workflow flowchart.
        
        Args:
            workflow_data: Workflow execution data
            show_execution_times: Whether to show execution times
            show_status: Whether to show agent status
            format: Output format ('png', 'svg', 'pdf')
            
        Returns:
            Path to saved flowchart
        """
        fig, ax = plt.subplots(1, 1, figsize=(16, 10))
        
        # Create agent nodes
        agent_nodes = self._parse_workflow_data(workflow_data)
        
        # Draw flowchart
        self._draw_flowchart(ax, agent_nodes, show_execution_times, show_status)
        
        # Customize plot
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 6)
        ax.axis('off')
        
        # Add title
        title = "Multi-Agent Resume Optimization Workflow"
        if show_execution_times and workflow_data.get('execution_time'):
            total_time = workflow_data['execution_time'].get('total', 0)
            title += f" (Total: {total_time:.2f}s)"
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        # Save plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"workflow_flowchart_{timestamp}.{format}"
        filepath = self.output_directory / filename
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight', 
                   facecolor=self.colors["background"])
        plt.close()
        
        logger.info(f"Workflow flowchart saved: {filepath}")
        return str(filepath)
    
    def _parse_workflow_data(self, workflow_data: Dict[str, Any]) -> List[AgentNode]:
        """Parse workflow data into AgentNode objects."""
        agents = []
        execution_times = workflow_data.get('execution_time', {})
        
        for i, (agent_name, agent_info) in enumerate(self.agents.items(), 1):
            status = "completed" if execution_times.get(agent_name.replace("Agent", "").lower()) else "pending"
            exec_time = execution_times.get(agent_name.replace("Agent", "").lower(), 0)
            
            node = AgentNode(
                name=agent_name,
                step=i,
                status=status,
                execution_time=exec_time,
                metadata=agent_info
            )
            agents.append(node)
        
        return agents
    
    def _draw_flowchart(self, ax, agent_nodes: List[AgentNode], 
                       show_execution_times: bool, show_status: bool) -> None:
        """Draw the workflow flowchart."""
        # Node positions (vertical layout)
        node_positions = [(5, 5), (5, 4), (5, 3), (5, 2), (5, 1)]
        
        # Draw nodes and connections
        for i, (node, pos) in enumerate(zip(agent_nodes, node_positions)):
            # Node color based on status
            if show_status:
                if node.status == "completed":
                    color = self.colors["success"]
                elif node.status == "failed":
                    color = self.colors["warning"]
                else:
                    color = self.colors["primary"]
            else:
                color = node.metadata["color"]
            
            # Draw node box
            node_box = FancyBboxPatch(
                (pos[0]-1.2, pos[1]-0.3), 2.4, 0.6,
                boxstyle="round,pad=0.1",
                facecolor=color,
                edgecolor='white',
                linewidth=2,
                alpha=0.8
            )
            ax.add_patch(node_box)
            
            # Node text
            node_text = f"{node.metadata['icon']} {node.name.replace('Agent', '')}"
            if show_execution_times and node.execution_time > 0:
                node_text += f"\n({node.execution_time:.2f}s)"
            
            ax.text(pos[0], pos[1], node_text, ha='center', va='center',
                   fontsize=10, fontweight='bold', color='white')
            
            # Draw arrows between nodes
            if i < len(agent_nodes) - 1:
                next_pos = node_positions[i + 1]
                arrow = patches.FancyArrowPatch(
                    (pos[0], pos[1]-0.3), (next_pos[0], next_pos[1]+0.3),
                    arrowstyle='->', mutation_scale=20,
                    color='gray', linewidth=2
                )
                ax.add_patch(arrow)
    
    def create_execution_timeline(
        self,
        workflow_data: Dict[str, Any],
        format: str = "png"
    ) -> str:
        """
        Create an execution timeline visualization.
        
        Args:
            workflow_data: Workflow execution data
            format: Output format ('png', 'svg', 'pdf')
            
        Returns:
            Path to saved timeline
        """
        execution_times = workflow_data.get('execution_time', {})
        
        if not execution_times:
            logger.warning("No execution time data available")
            return None
        
        # Prepare data
        steps = []
        times = []
        colors = []
        
        for agent_name, agent_info in self.agents.items():
            step_name = agent_name.replace("Agent", "")
            step_key = step_name.lower().replace("extractor", "job_data").replace("rag", "profile").replace("alignment", "content").replace("optimizer", "ats").replace("formatter", "latex")
            
            if step_key in execution_times:
                steps.append(step_name)
                times.append(execution_times[step_key])
                colors.append(agent_info["color"])
        
        # Create timeline
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        # Horizontal bar chart
        y_pos = range(len(steps))
        bars = ax1.barh(y_pos, times, color=colors, alpha=0.7)
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(steps, fontsize=12)
        ax1.set_xlabel('Execution Time (seconds)', fontsize=12)
        ax1.set_title('Workflow Step Execution Times', fontsize=14, fontweight='bold')
        
        # Add value labels on bars
        for i, (bar, time) in enumerate(zip(bars, times)):
            ax1.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
                    f'{time:.2f}s', va='center', fontsize=10)
        
        # Gantt chart
        start_time = 0
        for i, (step, time) in enumerate(zip(steps, times)):
            ax2.barh(i, time, left=start_time, color=colors[i], alpha=0.7, 
                    edgecolor='white', linewidth=1)
            ax2.text(start_time + time/2, i, f'{step}\n{time:.2f}s', 
                    ha='center', va='center', fontsize=10, color='white', fontweight='bold')
            start_time += time
        
        ax2.set_yticks(range(len(steps)))
        ax2.set_yticklabels(steps, fontsize=12)
        ax2.set_xlabel('Cumulative Time (seconds)', fontsize=12)
        ax2.set_title('Workflow Gantt Chart', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        # Save plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"execution_timeline_{timestamp}.{format}"
        filepath = self.output_directory / filename
        
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Execution timeline saved: {filepath}")
        return str(filepath)
    
    def create_ats_score_dashboard(
        self,
        workflow_data: Dict[str, Any],
        format: str = "html"
    ) -> str:
        """
        Create an interactive ATS score dashboard.
        
        Args:
            workflow_data: Workflow execution data
            format: Output format ('html', 'png', 'pdf')
            
        Returns:
            Path to saved dashboard
        """
        # Extract ATS data
        optimized_data = workflow_data.get('intermediate_results', {}).get('optimized_data', {})
        ats_analysis = optimized_data.get('ats_analysis', {})
        
        if not ats_analysis:
            logger.warning("No ATS analysis data available")
            return None
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Overall ATS Score', 'Keyword Density', 
                          'Section Completeness', 'Formatting Score'),
            specs=[[{"type": "indicator"}, {"type": "indicator"}],
                   [{"type": "indicator"}, {"type": "indicator"}]]
        )
        
        # Overall ATS Score
        ats_score = ats_analysis.get('ats_score', 0)
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=ats_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "ATS Score"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ),
            row=1, col=1
        )
        
        # Keyword Density
        keyword_density = ats_analysis.get('keyword_density', 0) * 100
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=keyword_density,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Keyword Density (%)"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkgreen"},
                    'steps': [
                        {'range': [0, 30], 'color': "lightgray"},
                        {'range': [30, 70], 'color': "yellow"},
                        {'range': [70, 100], 'color': "green"}
                    ]
                }
            ),
            row=1, col=2
        )
        
        # Section Completeness
        section_completeness = ats_analysis.get('section_completeness', 0) * 100
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=section_completeness,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Section Completeness (%)"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "purple"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "green"}
                    ]
                }
            ),
            row=2, col=1
        )
        
        # Formatting Score
        formatting_score = ats_analysis.get('formatting_score', 0) * 100
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=formatting_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Formatting Score (%)"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "orange"},
                    'steps': [
                        {'range': [0, 60], 'color': "lightgray"},
                        {'range': [60, 85], 'color': "yellow"},
                        {'range': [85, 100], 'color': "green"}
                    ]
                }
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            title="ATS Optimization Dashboard",
            font={'color': "darkblue", 'family': "Arial Black"}
        )
        
        # Save plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ats_dashboard_{timestamp}.{format}"
        filepath = self.output_directory / filename
        
        if format == "html":
            fig.write_html(filepath)
        else:
            fig.write_image(filepath)
        
        logger.info(f"ATS dashboard saved: {filepath}")
        return str(filepath)
    
    def create_agent_interaction_network(
        self,
        workflow_data: Dict[str, Any],
        format: str = "png"
    ) -> str:
        """
        Create a network diagram showing agent interactions.
        
        Args:
            workflow_data: Workflow execution data
            format: Output format ('png', 'svg', 'pdf')
            
        Returns:
            Path to saved network diagram
        """
        # Create directed graph
        G = nx.DiGraph()
        
        # Add nodes (agents)
        for agent_name, agent_info in self.agents.items():
            G.add_node(
                agent_name,
                color=agent_info["color"],
                icon=agent_info["icon"],
                description=agent_info["description"]
            )
        
        # Add edges (workflow sequence)
        agent_names = list(self.agents.keys())
        for i in range(len(agent_names) - 1):
            G.add_edge(agent_names[i], agent_names[i + 1])
        
        # Create layout
        try:
            pos = graphviz_layout(G, prog='dot')
        except:
            pos = nx.spring_layout(G, k=3, iterations=50)
        
        # Create plot
        fig, ax = plt.subplots(1, 1, figsize=(14, 10))
        
        # Draw nodes
        node_colors = [G.nodes[node]['color'] for node in G.nodes()]
        nx.draw_networkx_nodes(
            G, pos, node_color=node_colors, 
            node_size=3000, alpha=0.8, ax=ax
        )
        
        # Draw edges
        nx.draw_networkx_edges(
            G, pos, edge_color='gray', 
            arrows=True, arrowsize=20, 
            arrowstyle='->', ax=ax
        )
        
        # Draw labels
        labels = {}
        for node in G.nodes():
            icon = G.nodes[node]['icon']
            name = node.replace('Agent', '')
            labels[node] = f"{icon}\n{name}"
        
        nx.draw_networkx_labels(
            G, pos, labels, 
            font_size=10, font_weight='bold',
            font_color='white', ax=ax
        )
        
        # Add title and customize
        ax.set_title("Multi-Agent Interaction Network", 
                    fontsize=16, fontweight='bold', pad=20)
        ax.axis('off')
        
        # Save plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"agent_network_{timestamp}.{format}"
        filepath = self.output_directory / filename
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight',
                   facecolor=self.colors["background"])
        plt.close()
        
        logger.info(f"Agent interaction network saved: {filepath}")
        return str(filepath)
    
    def create_keyword_alignment_chart(
        self,
        workflow_data: Dict[str, Any],
        format: str = "png"
    ) -> str:
        """
        Create a keyword alignment visualization.
        
        Args:
            workflow_data: Workflow execution data
            format: Output format ('png', 'svg', 'pdf')
            
        Returns:
            Path to saved alignment chart
        """
        # Extract alignment data
        aligned_data = workflow_data.get('intermediate_results', {}).get('aligned_data', {})
        alignment_analysis = aligned_data.get('alignment_analysis', {})
        
        if not alignment_analysis:
            logger.warning("No alignment analysis data available")
            return None
        
        matched_keywords = alignment_analysis.get('matched_keywords', [])
        missing_keywords = alignment_analysis.get('missing_keywords', [])
        overall_score = alignment_analysis.get('overall_score', 0)
        
        # Create subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Keyword match pie chart
        labels = ['Matched', 'Missing']
        sizes = [len(matched_keywords), len(missing_keywords)]
        colors = [self.colors["success"], self.colors["warning"]]
        
        ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax1.set_title('Keyword Match Distribution', fontweight='bold')
        
        # Overall alignment score gauge
        ax2.text(0.5, 0.6, f'{overall_score:.1%}', ha='center', va='center',
                fontsize=48, fontweight='bold', color=self.colors["primary"])
        ax2.text(0.5, 0.4, 'Overall Alignment Score', ha='center', va='center',
                fontsize=14, fontweight='bold')
        ax2.set_xlim(0, 1)
        ax2.set_ylim(0, 1)
        ax2.axis('off')
        
        # Top matched keywords
        if matched_keywords:
            top_matched = matched_keywords[:10]  # Top 10
            y_pos = range(len(top_matched))
            ax3.barh(y_pos, [1] * len(top_matched), color=self.colors["success"], alpha=0.7)
            ax3.set_yticks(y_pos)
            ax3.set_yticklabels(top_matched, fontsize=10)
            ax3.set_title('Top Matched Keywords', fontweight='bold')
            ax3.set_xlabel('Count')
        
        # Missing keywords
        if missing_keywords:
            top_missing = missing_keywords[:10]  # Top 10
            y_pos = range(len(top_missing))
            ax4.barh(y_pos, [1] * len(top_missing), color=self.colors["warning"], alpha=0.7)
            ax4.set_yticks(y_pos)
            ax4.set_yticklabels(top_missing, fontsize=10)
            ax4.set_title('Missing Keywords', fontweight='bold')
            ax4.set_xlabel('Count')
        
        plt.suptitle('Keyword Alignment Analysis', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        # Save plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"keyword_alignment_{timestamp}.{format}"
        filepath = self.output_directory / filename
        
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Keyword alignment chart saved: {filepath}")
        return str(filepath)
    
    def create_comprehensive_report(
        self,
        workflow_data: Dict[str, Any],
        include_all_plots: bool = True
    ) -> Dict[str, str]:
        """
        Create a comprehensive visualization report with all plots.
        
        Args:
            workflow_data: Workflow execution data
            include_all_plots: Whether to include all available plots
            
        Returns:
            Dictionary mapping plot types to file paths
        """
        report_files = {}
        
        logger.info("Creating comprehensive visualization report...")
        
        try:
            # Workflow flowchart
            report_files['flowchart'] = self.create_workflow_flowchart(workflow_data)
        except Exception as e:
            logger.error(f"Failed to create flowchart: {e}")
        
        try:
            # Execution timeline
            if workflow_data.get('execution_time'):
                report_files['timeline'] = self.create_execution_timeline(workflow_data)
        except Exception as e:
            logger.error(f"Failed to create timeline: {e}")
        
        try:
            # Agent interaction network
            report_files['network'] = self.create_agent_interaction_network(workflow_data)
        except Exception as e:
            logger.error(f"Failed to create network: {e}")
        
        if include_all_plots:
            try:
                # ATS dashboard
                if workflow_data.get('intermediate_results', {}).get('optimized_data'):
                    report_files['ats_dashboard'] = self.create_ats_score_dashboard(workflow_data)
            except Exception as e:
                logger.error(f"Failed to create ATS dashboard: {e}")
            
            try:
                # Keyword alignment chart
                if workflow_data.get('intermediate_results', {}).get('aligned_data'):
                    report_files['alignment'] = self.create_keyword_alignment_chart(workflow_data)
            except Exception as e:
                logger.error(f"Failed to create alignment chart: {e}")
        
        # Create summary
        self._create_report_summary(workflow_data, report_files)
        
        logger.info(f"Comprehensive report created with {len(report_files)} visualizations")
        return report_files
    
    def _create_report_summary(self, workflow_data: Dict[str, Any], 
                              report_files: Dict[str, str]) -> None:
        """Create a summary file for the visualization report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = self.output_directory / f"visualization_summary_{timestamp}.json"
        
        summary = {
            "generated_at": datetime.now().isoformat(),
            "workflow_metadata": workflow_data.get('workflow_metadata', {}),
            "execution_summary": {
                "success": workflow_data.get('success', False),
                "total_time": workflow_data.get('execution_time', {}).get('total', 0),
                "errors": len(workflow_data.get('errors', [])),
                "warnings": len(workflow_data.get('warnings', []))
            },
            "visualizations": report_files,
            "output_directory": str(self.output_directory)
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Visualization summary saved: {summary_file}")


def main():
    """
    Main function for testing the WorkflowVisualizer.
    """
    print("WorkflowVisualizer Test")
    print("=" * 50)
    
    # Create sample workflow data
    sample_workflow_data = {
        "success": True,
        "execution_time": {
            "extract_job_data": 2.5,
            "retrieve_profile": 3.2,
            "align_content": 4.1,
            "optimize_ats": 2.8,
            "generate_latex": 1.9,
            "total": 14.5
        },
        "errors": [],
        "warnings": ["Minor formatting issue detected"],
        "workflow_metadata": {
            "job_url": "https://example.com/software-engineer",
            "profile_id": "test_user_123",
            "total_steps": 5,
            "completed_steps": 5
        },
        "intermediate_results": {
            "optimized_data": {
                "ats_analysis": {
                    "ats_score": 92,
                    "keyword_density": 0.75,
                    "section_completeness": 0.88,
                    "formatting_score": 0.95
                }
            },
            "aligned_data": {
                "alignment_analysis": {
                    "overall_score": 0.87,
                    "matched_keywords": ["Python", "JavaScript", "React", "Node.js", "SQL"],
                    "missing_keywords": ["Docker", "Kubernetes", "AWS"]
                }
            }
        }
    }
    
    try:
        # Initialize visualizer
        visualizer = WorkflowVisualizer(
            output_directory="output/visualizations",
            style="professional",
            color_scheme="blue"
        )
        
        print("Creating sample visualizations...")
        
        # Create individual visualizations
        flowchart_path = visualizer.create_workflow_flowchart(sample_workflow_data)
        print(f"✓ Flowchart: {flowchart_path}")
        
        timeline_path = visualizer.create_execution_timeline(sample_workflow_data)
        print(f"✓ Timeline: {timeline_path}")
        
        network_path = visualizer.create_agent_interaction_network(sample_workflow_data)
        print(f"✓ Network: {network_path}")
        
        ats_path = visualizer.create_ats_score_dashboard(sample_workflow_data)
        print(f"✓ ATS Dashboard: {ats_path}")
        
        alignment_path = visualizer.create_keyword_alignment_chart(sample_workflow_data)
        print(f"✓ Alignment Chart: {alignment_path}")
        
        # Create comprehensive report
        print("\nCreating comprehensive report...")
        report_files = visualizer.create_comprehensive_report(sample_workflow_data)
        
        print(f"\n✓ Comprehensive report created with {len(report_files)} visualizations")
        print(f"All files saved to: {visualizer.output_directory}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
