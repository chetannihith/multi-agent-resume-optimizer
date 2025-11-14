# Workflow Visualization Usage Guide

## Overview
The Multi-Agent Resume Optimizer now includes a comprehensive visualization system that creates beautiful charts, diagrams, and interactive dashboards to visualize the workflow execution, agent interactions, and performance metrics.

## Quick Start

### 1. Install Dependencies
First, make sure you have all the required visualization libraries:

```bash
pip install -r requirements.txt
```

The visualization system requires these additional packages:
- `matplotlib>=3.7.0` - For static plots and charts
- `seaborn>=0.12.0` - For statistical visualizations
- `plotly>=5.17.0` - For interactive dashboards
- `networkx>=3.1` - For network diagrams
- `pygraphviz>=1.11` - For advanced graph layouts

### 2. Basic Usage

#### Option A: Run the Demo Script
```bash
cd examples
python workflow_visualization_demo.py
```

#### Option B: Use with Your Own Workflow
```python
from src.workflow.workflow_visualizer import WorkflowVisualizer

# Initialize visualizer
visualizer = WorkflowVisualizer(
    output_directory="output/visualizations",
    style="professional",
    color_scheme="blue"
)

# Create visualizations from workflow data
workflow_data = {
    "success": True,
    "execution_time": {
        "extract_job_data": 2.5,
        "retrieve_profile": 3.2,
        "align_content": 4.1,
        "optimize_ats": 2.8,
        "generate_latex": 1.9,
        "total": 14.5
    },
    # ... your workflow data
}

# Create all visualizations
report_files = visualizer.create_comprehensive_report(workflow_data)
print(f"Created {len(report_files)} visualizations")
```

## Available Visualizations

### 1. Workflow Flowchart
Shows the complete workflow sequence with agent status and execution times.

```python
flowchart_path = visualizer.create_workflow_flowchart(
    workflow_data,
    show_execution_times=True,
    show_status=True
)
```

### 2. Execution Timeline
Displays step-by-step execution times with bar charts and Gantt charts.

```python
timeline_path = visualizer.create_execution_timeline(workflow_data)
```

### 3. Agent Interaction Network
Shows agent relationships and dependencies as a network diagram.

```python
network_path = visualizer.create_agent_interaction_network(workflow_data)
```

### 4. ATS Score Dashboard
Interactive dashboard with ATS optimization metrics (HTML format).

```python
ats_dashboard = visualizer.create_ats_score_dashboard(
    workflow_data,
    format="html"  # or "png", "svg", "pdf"
)
```

### 5. Keyword Alignment Chart
Shows keyword matching analysis with pie charts and keyword lists.

```python
alignment_chart = visualizer.create_keyword_alignment_chart(workflow_data)
```

## Integration with ResumeWorkflow

### Option 1: Use VisualizedResumeWorkflow (Recommended)
```python
from src.workflow.resume_workflow import VisualizedResumeWorkflow

# Initialize with visualization enabled
workflow = VisualizedResumeWorkflow(
    enable_visualization=True,
    visualization_style="professional",
    visualization_color_scheme="blue"
)

# Run workflow with automatic visualization
result = workflow.run_workflow_with_visualization(
    job_url="https://example.com/job",
    profile_id="candidate_123"
)

# Access visualization files
visualization_files = result["visualizations"]["files"]
```

### Option 2: Manual Integration
```python
from src.workflow.resume_workflow import ResumeWorkflow
from src.workflow.workflow_visualizer import WorkflowVisualizer

# Run workflow
workflow = ResumeWorkflow()
result = workflow.run_workflow(
    job_url="https://example.com/job",
    profile_id="candidate_123",
    return_intermediate_results=True
)

# Create visualizations
visualizer = WorkflowVisualizer()
report_files = visualizer.create_comprehensive_report(result)
```

## Running the Examples

### 1. Basic Visualization Demo
```bash
cd examples
python workflow_visualization_demo.py
```
This creates:
- Workflow flowcharts
- Execution timelines
- Agent interaction networks
- ATS score dashboards
- Keyword alignment charts
- Multiple color schemes
- Interactive HTML dashboards

### 2. Integration Demo
```bash
cd examples
python workflow_integration_demo.py
```
This demonstrates:
- Workflow integration with visualization
- Custom visualization creation
- Different style combinations
- Automatic visualization after workflow execution

### 3. Test Individual Components
```bash
cd src/workflow
python workflow_visualizer.py
```
This runs the built-in test with sample data.

## Customization Options

### Color Schemes
- `default`: Professional blue theme
- `blue`: Modern blue gradient  
- `green`: Fresh green theme

### Styles
- `professional`: Clean, business-focused
- `modern`: Contemporary design
- `minimal`: Simple, focused

### Output Formats
- `png`: High-quality raster images (default)
- `svg`: Scalable vector graphics
- `pdf`: Print-ready documents
- `html`: Interactive dashboards (for ATS dashboard)

## Output Files

All visualizations are saved to `output/visualizations/` by default:

```
output/visualizations/
├── workflow_flowchart_20250102_143022.png
├── execution_timeline_20250102_143022.png
├── agent_network_20250102_143022.png
├── ats_dashboard_20250102_143022.html
├── keyword_alignment_20250102_143022.png
└── visualization_summary_20250102_143022.json
```

## Troubleshooting

### Common Issues

1. **Missing Dependencies**
   ```bash
   pip install matplotlib seaborn plotly networkx pygraphviz
   ```

2. **Graphviz Not Found**
   - Windows: Install Graphviz from https://graphviz.org/download/
   - Linux: `sudo apt-get install graphviz graphviz-dev`
   - macOS: `brew install graphviz`

3. **No Data Available**
   - Ensure workflow data includes execution times and intermediate results
   - Check that `return_intermediate_results=True` when running workflow

4. **Permission Errors**
   - Ensure output directory is writable
   - Check file permissions

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# This will show detailed logs
visualizer = WorkflowVisualizer()
```

## Advanced Usage

### Custom Visualization Settings
```python
# Create custom flowchart
flowchart = visualizer.create_workflow_flowchart(
    workflow_data,
    show_execution_times=True,
    show_status=True,
    format="svg"  # High-quality vector format
)

# Create interactive dashboard
dashboard = visualizer.create_ats_score_dashboard(
    workflow_data,
    format="html"  # Interactive format
)
```

### Batch Processing
```python
# Process multiple workflow results
workflow_results = [result1, result2, result3]

for i, result in enumerate(workflow_results):
    visualizer = WorkflowVisualizer(
        output_directory=f"output/batch_{i}"
    )
    report_files = visualizer.create_comprehensive_report(result)
```

## Integration with Streamlit

```python
import streamlit as st
from src.workflow.resume_workflow import VisualizedResumeWorkflow

st.title("Resume Optimization Workflow")

if st.button("Run Workflow"):
    workflow = VisualizedResumeWorkflow(enable_visualization=True)
    result = workflow.run_workflow_with_visualization(job_url, profile_id)
    
    # Display visualizations
    if result["visualizations"]["summary"]["success"]:
        for viz_type, file_path in result["visualizations"]["files"].items():
            if file_path.endswith('.html'):
                st.components.v1.iframe(file_path, height=600)
            else:
                st.image(file_path)
```

## Performance Tips

1. **Use PNG for presentations** - High quality, good compression
2. **Use SVG for documents** - Scalable, small file size
3. **Use HTML for dashboards** - Interactive, best for web
4. **Disable visualization in production** if not needed
5. **Cache visualizations** for repeated workflow runs

## Next Steps

1. Run the demo scripts to see all visualizations
2. Integrate with your workflow using `VisualizedResumeWorkflow`
3. Customize colors and styles for your branding
4. Use interactive dashboards for stakeholder presentations
5. Check the generated files in `output/visualizations/`
