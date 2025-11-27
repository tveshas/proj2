"""Data visualization tools."""
import logging
import base64
import io
from typing import Dict, Any, List, Optional
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px

logger = logging.getLogger(__name__)


async def create_chart(
    data: List[Dict[str, Any]], 
    chart_type: str, 
    x: Optional[str] = None,
    y: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a chart from data.
    
    Args:
        data: List of dictionaries representing rows
        chart_type: Type of chart (bar, line, scatter, pie, etc.)
        x: X-axis column name
        y: Y-axis column name
        **kwargs: Additional chart parameters
        
    Returns:
        Dict with base64 encoded image
    """
    try:
        import pandas as pd
        df = pd.DataFrame(data)
        
        if chart_type == "bar":
            if x and y:
                fig = px.bar(df, x=x, y=y, **kwargs)
            else:
                return {"error": "x and y columns required for bar chart"}
        
        elif chart_type == "line":
            if x and y:
                fig = px.line(df, x=x, y=y, **kwargs)
            else:
                return {"error": "x and y columns required for line chart"}
        
        elif chart_type == "scatter":
            if x and y:
                fig = px.scatter(df, x=x, y=y, **kwargs)
            else:
                return {"error": "x and y columns required for scatter chart"}
        
        elif chart_type == "pie":
            if x and y:
                fig = px.pie(df, names=x, values=y, **kwargs)
            else:
                return {"error": "x and y columns required for pie chart"}
        
        else:
            return {"error": f"Unknown chart type: {chart_type}"}
        
        # Convert to base64
        img_bytes = fig.to_image(format="png")
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        
        return {
            "image": f"data:image/png;base64,{img_base64}",
            "chart_type": chart_type
        }
        
    except Exception as e:
        logger.error(f"Error creating chart: {e}")
        return {"error": str(e)}


async def create_matplotlib_chart(
    data: List[Dict[str, Any]],
    chart_type: str,
    x: Optional[str] = None,
    y: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a matplotlib chart (alternative to plotly).
    
    Args:
        data: List of dictionaries representing rows
        chart_type: Type of chart
        x: X-axis column name
        y: Y-axis column name
        **kwargs: Additional parameters
        
    Returns:
        Dict with base64 encoded image
    """
    try:
        import pandas as pd
        df = pd.DataFrame(data)
        
        plt.figure(figsize=(10, 6))
        
        if chart_type == "bar":
            if x and y:
                plt.bar(df[x], df[y])
                plt.xlabel(x)
                plt.ylabel(y)
            else:
                return {"error": "x and y columns required"}
        
        elif chart_type == "line":
            if x and y:
                plt.plot(df[x], df[y])
                plt.xlabel(x)
                plt.ylabel(y)
            else:
                return {"error": "x and y columns required"}
        
        elif chart_type == "scatter":
            if x and y:
                plt.scatter(df[x], df[y])
                plt.xlabel(x)
                plt.ylabel(y)
            else:
                return {"error": "x and y columns required"}
        
        else:
            return {"error": f"Unknown chart type: {chart_type}"}
        
        plt.title(kwargs.get("title", "Chart"))
        plt.tight_layout()
        
        # Convert to base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        return {
            "image": f"data:image/png;base64,{img_base64}",
            "chart_type": chart_type
        }
        
    except Exception as e:
        logger.error(f"Error creating matplotlib chart: {e}")
        plt.close()
        return {"error": str(e)}

