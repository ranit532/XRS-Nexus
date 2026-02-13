#!/usr/bin/env python3
"""
Lineage Visualization
Generates interactive HTML visualizations of data lineage from ADF pipelines
"""

import json
import sys
from pathlib import Path
from typing import Dict, List
from datetime import datetime

class LineageVisualizer:
    """Visualizes data lineage as Mermaid diagrams"""
    
    def __init__(self, lineage_file: Path):
        with open(lineage_file, 'r') as f:
            self.lineage_data = json.load(f)
    
    def generate_mermaid_diagram(self) -> str:
        """Generate Mermaid flowchart from lineage graph"""
        graph = self.lineage_data.get("lineage_graph", {})
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        
        mermaid = ["flowchart LR"]
        
        # Add nodes with styling
        for node in nodes:
            node_id = self._sanitize_id(node["id"])
            node_label = node["id"]
            node_type = node.get("type", "unknown")
            
            # Style based on type
            if node_type == "dataset":
                layer = node.get("layer", "")
                if layer == "source":
                    mermaid.append(f'    {node_id}[("{node_label}<br/>📁 Source")]:::sourceStyle')
                else:
                    mermaid.append(f'    {node_id}[("{node_label}<br/>💾 Sink")]:::sinkStyle')
            elif node_type == "Copy":
                mermaid.append(f'    {node_id}["{node_label}<br/>📋 Copy"]:::copyStyle')
            elif node_type == "ExecuteDataFlow":
                mermaid.append(f'    {node_id}["{node_label}<br/>🔄 Transform"]:::transformStyle')
            else:
                mermaid.append(f'    {node_id}["{node_label}"]')
        
        # Add edges
        for edge in edges:
            from_id = self._sanitize_id(edge["from"])
            to_id = self._sanitize_id(edge["to"])
            edge_type = edge.get("type", "")
            
            if edge_type == "reads":
                mermaid.append(f'    {from_id} -->|reads| {to_id}')
            elif edge_type == "writes":
                mermaid.append(f'    {from_id} -->|writes| {to_id}')
            else:
                mermaid.append(f'    {from_id} --> {to_id}')
        
        # Add styling
        mermaid.extend([
            "",
            "    classDef sourceStyle fill:#e1f5ff,stroke:#01579b,stroke-width:2px",
            "    classDef sinkStyle fill:#f3e5f5,stroke:#4a148c,stroke-width:2px",
            "    classDef copyStyle fill:#fff3e0,stroke:#e65100,stroke-width:2px",
            "    classDef transformStyle fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px"
        ])
        
        return "\n".join(mermaid)
    
    def _sanitize_id(self, node_id: str) -> str:
        """Sanitize node ID for Mermaid compatibility"""
        if node_id is None:
            return "unknown_node"
        return str(node_id).replace("/", "_").replace(".", "_").replace("-", "_")
    
    def generate_html(self, output_file: Path):
        """Generate standalone HTML file with Mermaid visualization"""
        mermaid_diagram = self.generate_mermaid_diagram()
        metadata = self.lineage_data.get("metadata", {})
        pipeline_run = self.lineage_data.get("pipeline_run", {})
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ADF Pipeline Lineage - {metadata.get('pipeline_name', 'Unknown')}</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #0078d4 0%, #005a9e 100%);
            color: white;
            padding: 30px;
        }}
        
        .header h1 {{
            font-size: 32px;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            font-size: 16px;
            opacity: 0.9;
        }}
        
        .metadata {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f5f5f5;
            border-bottom: 1px solid #ddd;
        }}
        
        .metadata-item {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .metadata-item .label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 5px;
        }}
        
        .metadata-item .value {{
            font-size: 18px;
            font-weight: 600;
            color: #333;
        }}
        
        .status-success {{
            color: #2e7d32;
        }}
        
        .status-failed {{
            color: #c62828;
        }}
        
        .diagram-container {{
            padding: 40px;
            background: white;
        }}
        
        .diagram-title {{
            font-size: 24px;
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #0078d4;
        }}
        
        .mermaid {{
            display: flex;
            justify-content: center;
            padding: 20px;
            background: #fafafa;
            border-radius: 8px;
        }}
        
        .footer {{
            padding: 20px 30px;
            background: #f5f5f5;
            text-align: center;
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔄 Data Pipeline Lineage</h1>
            <div class="subtitle">Azure Data Factory - XRS NEXUS Platform</div>
        </div>
        
        <div class="metadata">
            <div class="metadata-item">
                <div class="label">Pipeline Name</div>
                <div class="value">{pipeline_run.get('pipeline_name', 'N/A')}</div>
            </div>
            <div class="metadata-item">
                <div class="label">Run ID</div>
                <div class="value" style="font-size: 14px;">{metadata.get('run_id', 'N/A')[:16]}...</div>
            </div>
            <div class="metadata-item">
                <div class="label">Status</div>
                <div class="value status-{pipeline_run.get('status', 'unknown').lower()}">{pipeline_run.get('status', 'N/A')}</div>
            </div>
            <div class="metadata-item">
                <div class="label">Duration</div>
                <div class="value">{pipeline_run.get('duration_seconds', 0):.2f}s</div>
            </div>
            <div class="metadata-item">
                <div class="label">Start Time</div>
                <div class="value" style="font-size: 14px;">{pipeline_run.get('run_start', 'N/A')[:19] if pipeline_run.get('run_start') else 'N/A'}</div>
            </div>
            <div class="metadata-item">
                <div class="label">Captured At</div>
                <div class="value" style="font-size: 14px;">{metadata.get('captured_at', 'N/A')[:19] if metadata.get('captured_at') else 'N/A'}</div>
            </div>
        </div>
        
        <div class="diagram-container">
            <h2 class="diagram-title">📊 Data Flow Lineage</h2>
            <div class="mermaid">
{mermaid_diagram}
            </div>
        </div>
        
        <div class="footer">
            Generated by XRS NEXUS Lineage Tracker | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
    
    <script>
        mermaid.initialize({{ 
            startOnLoad: true,
            theme: 'default',
            flowchart: {{
                useMaxWidth: true,
                htmlLabels: true,
                curve: 'basis'
            }}
        }});
    </script>
</body>
</html>"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Generated lineage visualization: {output_file}")

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python visualize_lineage.py <lineage_json_file> [output_html]")
        sys.exit(1)
    
    lineage_file = Path(sys.argv[1])
    if not lineage_file.exists():
        print(f"❌ Lineage file not found: {lineage_file}")
        sys.exit(1)
    
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else lineage_file.with_suffix('.html')
    
    visualizer = LineageVisualizer(lineage_file)
    visualizer.generate_html(output_file)
    
    print(f"\n🎉 Lineage visualization complete!")
    print(f"📂 Open in browser: file://{output_file.absolute()}")

if __name__ == "__main__":
    main()
