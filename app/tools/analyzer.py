"""Data analysis tools."""
import logging
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


async def analyze_dataframe(data: List[Dict[str, Any]], operation: str, **kwargs) -> Dict[str, Any]:
    """
    Perform data analysis operations on a DataFrame.
    
    Args:
        data: List of dictionaries representing rows
        operation: Operation to perform (sum, mean, count, filter, groupby, etc.)
        **kwargs: Additional parameters for the operation
        
    Returns:
        Result of the operation
    """
    try:
        df = pd.DataFrame(data)
        
        if operation == "sum":
            column = kwargs.get("column")
            if column:
                return {"result": float(df[column].sum())}
            return {"error": "Column name required for sum"}
        
        elif operation == "mean":
            column = kwargs.get("column")
            if column:
                return {"result": float(df[column].mean())}
            return {"error": "Column name required for mean"}
        
        elif operation == "count":
            return {"result": len(df)}
        
        elif operation == "filter":
            # Filter by conditions
            filtered = df.copy()
            for key, value in kwargs.items():
                if key != "operation":
                    filtered = filtered[filtered[key] == value]
            return {"result": filtered.to_dict('records'), "count": len(filtered)}
        
        elif operation == "groupby":
            by = kwargs.get("by")
            agg = kwargs.get("agg", "count")
            if by:
                grouped = df.groupby(by).agg(agg)
                return {"result": grouped.to_dict()}
            return {"error": "Group by column required"}
        
        elif operation == "sort":
            by = kwargs.get("by")
            ascending = kwargs.get("ascending", True)
            if by:
                sorted_df = df.sort_values(by=by, ascending=ascending)
                return {"result": sorted_df.to_dict('records')}
            return {"error": "Sort column required"}
        
        else:
            return {"error": f"Unknown operation: {operation}"}
            
    except Exception as e:
        logger.error(f"Error in analysis: {e}")
        return {"error": str(e)}


async def calculate_statistics(data: List[Dict[str, Any]], column: str) -> Dict[str, Any]:
    """
    Calculate statistics for a numeric column.
    
    Args:
        data: List of dictionaries representing rows
        column: Column name to analyze
        
    Returns:
        Dict with statistics
    """
    try:
        df = pd.DataFrame(data)
        if column not in df.columns:
            return {"error": f"Column {column} not found"}
        
        stats = df[column].describe()
        return {
            "count": int(stats['count']),
            "mean": float(stats['mean']),
            "std": float(stats['std']),
            "min": float(stats['min']),
            "max": float(stats['max']),
            "median": float(df[column].median()),
            "sum": float(df[column].sum())
        }
    except Exception as e:
        logger.error(f"Error calculating statistics: {e}")
        return {"error": str(e)}

