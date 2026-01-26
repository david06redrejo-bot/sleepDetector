"""
utils/geometry.py

Geometric utility functions for calculating distances and aspect ratios.
"""

import math
from typing import Tuple, List

def euclidean_distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """
    Calculates the Euclidean distance (L2 Norm) between two 2D points.

    Args:
        point1: Tuple (x, y)
        point2: Tuple (x, y)

    Returns:
        float: The distance between the points.
    """
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def calculate_ear(eye_landmarks: List[Tuple[float, float]]) -> float:
    """
    Calculates the Eye Aspect Ratio (EAR) for a single eye.
    
    The EAR is a scalar value that remains approximately constant while the
    eye is open, but tends to zero as the eye closes.

    Args:
        eye_landmarks: List of 6 (x, y) tuples.
    
    Returns:
        float: The EAR value.
    """
    # Unpack landmarks (Crow-Plexis format, specific indices)
    p1, p2, p3, p4, p5, p6 = eye_landmarks

    # Vertical distances
    vert1 = euclidean_distance(p2, p6)
    vert2 = euclidean_distance(p3, p5)

    # Horizontal distance
    horiz = euclidean_distance(p1, p4)

    # Prevent division by zero
    if horiz == 0:
        return 0.0

    # EAR Formula
    return (vert1 + vert2) / (2.0 * horiz)
