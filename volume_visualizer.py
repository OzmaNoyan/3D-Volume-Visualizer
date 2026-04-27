"""
Volume Visualizer for Calculus Cross-Sections
==============================================
A tool for visualizing volumes of solids formed by stacking cross-sections
perpendicular to an interval [a, b], where the cross-sectional area depends
on a function f(x).

This program:
1. Takes a function f(x), interval [a, b], and cross-section type as input
2. Computes an approximate volume using Riemann sums
3. Displays 2D and 3D visualizations of the solid
4. Compares with the exact integral (if possible)

Author: Calculus Learning Tool
Date: 2024
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
import math
from typing import Callable, Tuple, List
import warnings

warnings.filterwarnings('ignore')

# ============================================================================
# STEP 1: FUNCTION PARSING AND VALIDATION
# ============================================================================

def parse_function(func_str: str) -> Callable[[float], float]:
    """
    Parse a string representation of a function and return a callable function.
    
    Args:
        func_str: String representation like "x**2", "sin(x)", "sqrt(x)", etc.
    
    Returns:
        A callable function that takes x and returns f(x)
    
    Example:
        >>> f = parse_function("x**2")
        >>> f(2)
        4
    """
    # Create a safe namespace with common math functions
    safe_dict = {
        'sin': np.sin,
        'cos': np.cos,
        'tan': np.tan,
        'sqrt': np.sqrt,
        'exp': np.exp,
        'log': np.log,
        'log10': np.log10,
        'abs': np.abs,
        'pi': np.pi,
        'e': np.e,
    }
    
    def f(x):
        try:
            # Evaluate the function string with x as a variable
            result = eval(func_str, {"__builtins__": {}}, {**safe_dict, 'x': x})
            return float(result)
        except Exception as e:
            raise ValueError(f"Error evaluating function '{func_str}' at x={x}: {str(e)}")
    
    # Test the function with a sample value
    try:
        test_val = f(1.0)
        if np.isnan(test_val) or np.isinf(test_val):
            raise ValueError("Function returned NaN or infinity at test point")
    except Exception as e:
        raise ValueError(f"Invalid function: {func_str}. Error: {str(e)}")
    
    return f


def validate_input(a: float, b: float, n: int, cross_section: str) -> bool:
    """
    Validate user inputs for the volume calculation.
    
    Args:
        a: Left endpoint of interval
        b: Right endpoint of interval
        n: Number of slices
        cross_section: Type of cross-section ("square", "semicircle", "triangle")
    
    Returns:
        True if all inputs are valid, raises ValueError otherwise
    """
    if a >= b:
        raise ValueError("Left endpoint a must be less than right endpoint b")
    
    if n < 1:
        raise ValueError("Number of slices must be at least 1")
    
    if cross_section not in ["square", "semicircle", "triangle"]:
        raise ValueError("Cross-section must be 'square', 'semicircle', or 'triangle'")
    
    return True


# ============================================================================
# STEP 2: CROSS-SECTIONAL AREA COMPUTATION
# ============================================================================

def compute_area(radius: float, cross_section: str) -> float:
    """
    Compute the area of a cross-section given the radius (height of function).
    
    The radius is the value of f(x) at a given point. Different shapes have
    different area formulas:
    
    - Square: Side length = f(x), so A = (f(x))^2
    - Semicircle: Diameter = f(x), so A = (π/8) * (f(x))^2
    - Equilateral Triangle: Side = f(x), so A = (√3/4) * (f(x))^2
    
    Args:
        radius: The value of f(x) (used as the dimension for the cross-section)
        cross_section: Type of cross-section
    
    Returns:
        The area of the cross-section
    """
    if radius < 0:
        radius = abs(radius)  # Handle negative function values
    
    if cross_section == "square":
        # Square with side length = radius
        return radius ** 2
    
    elif cross_section == "semicircle":
        # Semicircle with diameter = radius
        # Area of semicircle = (1/2) * π * r² where r = radius/2
        return (np.pi / 8) * (radius ** 2)
    
    elif cross_section == "triangle":
        # Equilateral triangle with side length = radius
        # Area = (√3/4) * s² where s = side length
        return (np.sqrt(3) / 4) * (radius ** 2)
    
    else:
        raise ValueError(f"Unknown cross-section type: {cross_section}")


# ============================================================================
# STEP 3: VOLUME APPROXIMATION
# ============================================================================

def approximate_volume(f: Callable, a: float, b: float, n: int, 
                      cross_section: str) -> Tuple[float, np.ndarray, np.ndarray, np.ndarray]:
    """
    Approximate the volume of a solid using Riemann sums.
    
    The volume is approximated by:
    V ≈ Σ A(x_i) * dx
    
    where:
    - A(x_i) is the cross-sectional area at point x_i
    - dx is the width of each slice
    - The sum is over all n slices
    
    Args:
        f: The function f(x)
        a: Left endpoint of interval
        b: Right endpoint of interval
        n: Number of slices (subintervals)
        cross_section: Type of cross-section
    
    Returns:
        Tuple containing:
        - volume: Approximate volume
        - x_values: Array of x values at slice centers
        - areas: Array of cross-sectional areas
        - endpoints: Array of interval endpoints
    """
    # Compute the width of each slice
    dx = (b - a) / n
    
    # Create array of interval endpoints
    endpoints = np.linspace(a, b, n + 1)
    
    # Create array of slice centers (where we evaluate f(x))
    x_values = (endpoints[:-1] + endpoints[1:]) / 2
    
    # Compute function values at each slice center
    f_values = np.array([f(x) for x in x_values])
    
    # Compute cross-sectional areas
    areas = np.array([compute_area(f_val, cross_section) for f_val in f_values])
    
    # Compute volume as sum of (area × width)
    volume = np.sum(areas * dx)
    
    return volume, x_values, areas, endpoints


def compute_exact_volume(f_str: str, a: float, b: float, cross_section: str) -> float:
    """
    Attempt to compute the exact volume using symbolic integration with sympy.
    
    Args:
        f_str: String representation of function
        a: Left endpoint
        b: Right endpoint
        cross_section: Type of cross-section
    
    Returns:
        The exact volume, or None if integration fails
    """
    try:
        import sympy as sp
        
        # Define symbolic variable
        x = sp.Symbol('x')
        
        # Parse the function string symbolically
        safe_dict = {
            'sin': sp.sin,
            'cos': sp.cos,
            'tan': sp.tan,
            'sqrt': sp.sqrt,
            'exp': sp.exp,
            'log': sp.log,
            'log10': sp.log10,
            'abs': sp.Abs,
            'pi': sp.pi,
            'e': sp.e,
        }
        
        f_sym = eval(f_str, {"__builtins__": {}}, {**safe_dict, 'x': x})
        
        # Compute the cross-sectional area function
        if cross_section == "square":
            area_func = f_sym ** 2
        elif cross_section == "semicircle":
            area_func = (sp.pi / 8) * (f_sym ** 2)
        elif cross_section == "triangle":
            area_func = (sp.sqrt(3) / 4) * (f_sym ** 2)
        
        # Integrate to find exact volume
        exact_volume = sp.integrate(area_func, (x, a, b))
        
        return float(exact_volume.evalf())
    
    except ImportError:
        return None
    except Exception as e:
        print(f"  (Could not compute exact integral: {str(e)})")
        return None


# ============================================================================
# STEP 4: 2D VISUALIZATION
# ============================================================================

def plot_2d(f: Callable, a: float, b: float, x_centers: np.ndarray, 
            areas: np.ndarray, endpoints: np.ndarray, cross_section: str):
    """
    Create a 2D visualization showing the function and the slices.
    
    This plot shows:
    - The function f(x) as a smooth curve
    - Vertical lines representing the slices
    - The endpoints of the interval
    
    Args:
        f: The function to plot
        a: Left endpoint
        b: Right endpoint
        x_centers: X-coordinates of slice centers
        areas: Cross-sectional areas (for reference)
        endpoints: Interval endpoints
        cross_section: Type of cross-section (for title)
    """
    # Create a dense array of x values for smooth curve
    x_plot = np.linspace(a, b, 500)
    y_plot = np.array([f(x) for x in x_plot])
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 5))
    
    # Plot the function curve
    ax.plot(x_plot, y_plot, 'b-', linewidth=2.5, label='f(x)')
    ax.fill_between(x_plot, 0, y_plot, alpha=0.2, color='blue')
    
    # Draw vertical slices
    colors = plt.cm.rainbow(np.linspace(0, 1, len(x_centers)))
    for i, (x_center, endpoint_left, endpoint_right) in enumerate(
        zip(x_centers, endpoints[:-1], endpoints[1:])):
        
        y_val = f(x_center)
        
        # Draw vertical line at slice center
        ax.plot([x_center, x_center], [0, y_val], 'r--', alpha=0.6, linewidth=1.5)
        
        # Draw rectangle showing the slice
        ax.add_patch(plt.Rectangle(
            (endpoint_left, 0), endpoint_right - endpoint_left, y_val,
            alpha=0.1, color=colors[i], edgecolor='red', linewidth=1))
    
    # Formatting
    ax.set_xlabel('x', fontsize=12, fontweight='bold')
    ax.set_ylabel('f(x)', fontsize=12, fontweight='bold')
    ax.set_title(
        f'Function f(x) with {len(x_centers)} Slices\n'
        f'Cross-Section Type: {cross_section.capitalize()}',
        fontsize=14, fontweight='bold'
    )
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=11)
    ax.set_xlim(a - 0.1*(b-a), b + 0.1*(b-a))
    
    plt.tight_layout()
    return fig


# ============================================================================
# STEP 5: 3D VISUALIZATION
# ============================================================================

def plot_3d(f: Callable, a: float, b: float, n: int, cross_section: str):
    """
    Create a 3D visualization of the solid formed by stacking cross-sections.
    
    This plot shows the actual solid, where:
    - The x-axis represents the interval [a, b]
    - The y and z axes represent the dimensions of the cross-section
    - The cross-sections are stacked along the x-axis
    
    Args:
        f: The function to plot
        a: Left endpoint
        b: Right endpoint
        n: Number of slices
        cross_section: Type of cross-section
    """
    # Create figure with 3D projection
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Number of points per cross-section
    theta_points = 100
    
    # Create slices
    dx = (b - a) / n
    x_slice_centers = np.linspace(a + dx/2, b - dx/2, n)
    
    # For each slice, create a cross-section and draw it
    colors = plt.cm.rainbow(np.linspace(0, 1, n))
    
    for i, x_val in enumerate(x_slice_centers):
        r = abs(f(x_val))  # Radius/half-width of the cross-section
        
        if cross_section == "square":
            # Draw a square cross-section
            square_y = np.array([-r/2, r/2, r/2, -r/2, -r/2])
            square_z = np.array([-r/2, -r/2, r/2, r/2, -r/2])
            square_x = np.full_like(square_y, x_val)
            
            ax.plot(square_x, square_y, square_z, color=colors[i], linewidth=1)
            
            # Fill the square
            for j in range(len(square_x) - 1):
                ax.plot(
                    [square_x[j], square_x[j+1]],
                    [square_y[j], square_y[j+1]],
                    [square_z[j], square_z[j+1]],
                    color=colors[i], linewidth=1.5
                )
        
        elif cross_section == "semicircle":
            # Draw a semicircular cross-section
            theta = np.linspace(0, np.pi, theta_points)
            semicircle_y = r * np.cos(theta)
            semicircle_z = r * np.sin(theta)
            semicircle_x = np.full_like(semicircle_y, x_val)
            
            ax.plot(semicircle_x, semicircle_y, semicircle_z, color=colors[i], linewidth=1.5)
            
            # Close the semicircle with diameter line
            ax.plot([x_val, x_val], [-r, r], [0, 0], color=colors[i], linewidth=1.5)
        
        elif cross_section == "triangle":
            # Draw an equilateral triangle cross-section
            h = r * np.sqrt(3) / 2  # Height of equilateral triangle
            triangle_y = np.array([0, r/2, -r/2, 0])
            triangle_z = np.array([h, -r/(2*np.sqrt(3)), -r/(2*np.sqrt(3)), h])
            triangle_x = np.full_like(triangle_y, x_val)
            
            ax.plot(triangle_x, triangle_y, triangle_z, color=colors[i], linewidth=1.5)
    
    # Draw the outline of the solid
    x_outline = np.linspace(a, b, n * 5)
    f_vals = np.array([abs(f(x)) for x in x_outline])
    
    if cross_section == "square":
        ax.plot(x_outline, f_vals/2, 0 * f_vals, 'k-', alpha=0.3, linewidth=1)
        ax.plot(x_outline, -f_vals/2, 0 * f_vals, 'k-', alpha=0.3, linewidth=1)
        ax.plot(x_outline, 0 * f_vals, f_vals/2, 'k-', alpha=0.3, linewidth=1)
        ax.plot(x_outline, 0 * f_vals, -f_vals/2, 'k-', alpha=0.3, linewidth=1)
    
    # Formatting
    ax.set_xlabel('x', fontsize=11, fontweight='bold')
    ax.set_ylabel('y', fontsize=11, fontweight='bold')
    ax.set_zlabel('z', fontsize=11, fontweight='bold')
    ax.set_title(
        f'3D Solid: {cross_section.capitalize()} Cross-Sections\n'
        f'Interval: [{a:.2f}, {b:.2f}], Slices: {n}',
        fontsize=13, fontweight='bold'
    )
    
    # Set equal aspect ratio for better visualization
    max_range = max([abs(f(x)) for x in np.linspace(a, b, 50)]) / 2
    ax.set_xlim(a, b)
    ax.set_ylim(-max_range, max_range)
    ax.set_zlim(-max_range, max_range)
    
    return fig


# ============================================================================
# STEP 6: USER INTERACTION
# ============================================================================

def get_user_input() -> Tuple[str, float, float, int, str]:
    """
    Prompt the user for input and return validated inputs.
    
    Returns:
        Tuple of (function_string, a, b, n, cross_section)
    """
    print("\n" + "="*70)
    print(" VOLUME OF SOLIDS WITH KNOWN CROSS-SECTIONS")
    print("="*70)
    
    # Get function
    print("\n1. Enter a function f(x) as a string:")
    print("   Examples: 'x**2', 'sin(x)', 'sqrt(x)', '2*x', 'exp(x)'")
    print("   Allowed functions: sin, cos, tan, sqrt, exp, log, log10, abs")
    func_str = input("   f(x) = ").strip()
    
    if not func_str:
        raise ValueError("Function cannot be empty")
    
    # Get interval
    print("\n2. Enter the interval [a, b]:")
    try:
        a = float(input("   Left endpoint a = "))
        b = float(input("   Right endpoint b = "))
    except ValueError:
        raise ValueError("Endpoints must be numbers")
    
    # Get number of slices
    print("\n3. Enter the number of slices:")
    print("   (More slices = more accurate, but slower)")
    try:
        n = int(input("   Number of slices n = "))
    except ValueError:
        raise ValueError("Number of slices must be an integer")
    
    # Get cross-section type
    print("\n4. Choose cross-section type:")
    print("   a) square")
    print("   b) semicircle")
    print("   c) triangle (equilateral)")
    choice = input("   Enter choice (a/b/c or full name) = ").strip().lower()
    
    cross_section_map = {
        'a': 'square',
        'b': 'semicircle',
        'c': 'triangle',
        'square': 'square',
        'semicircle': 'semicircle',
        'triangle': 'triangle'
    }
    
    if choice not in cross_section_map:
        raise ValueError("Invalid choice for cross-section")
    
    cross_section = cross_section_map[choice]
    
    return func_str, a, b, n, cross_section


def print_results(volume: float, exact_volume: float = None, n: int = None, 
                 cross_section: str = ""):
    """
    Print the results in a formatted manner.
    
    Args:
        volume: Approximate volume computed
        exact_volume: Exact volume (if available)
        n: Number of slices used
        cross_section: Type of cross-section
    """
    print("\n" + "="*70)
    print(" RESULTS")
    print("="*70)
    
    print(f"\nApproximate Volume (using {n} slices):")
    print(f"  V ≈ {volume:.10f} cubic units")
    
    if exact_volume is not None:
        error = abs(volume - exact_volume)
        percent_error = (error / abs(exact_volume)) * 100 if exact_volume != 0 else 0
        
        print(f"\nExact Volume (from symbolic integration):")
        print(f"  V = {exact_volume:.10f} cubic units")
        print(f"\nError Analysis:")
        print(f"  Absolute Error: {error:.10e} cubic units")
        print(f"  Relative Error: {percent_error:.4f}%")
    
    print("\n" + "="*70)


# ============================================================================
# STEP 7: MAIN PROGRAM
# ============================================================================

def main():
    """
    Main program flow.
    """
    try:
        # Get user input
        func_str, a, b, n, cross_section = get_user_input()
        
        # Validate input
        validate_input(a, b, n, cross_section)
        
        # Parse the function
        print("\nProcessing... Please wait.")
        f = parse_function(func_str)
        
        # Compute approximate volume
        volume, x_centers, areas, endpoints = approximate_volume(f, a, b, n, cross_section)
        
        # Try to compute exact volume
        exact_volume = compute_exact_volume(func_str, a, b, cross_section)
        
        # Print results
        print_results(volume, exact_volume, n, cross_section)
        
        # Create visualizations
        print("\nGenerating 2D visualization...")
        fig_2d = plot_2d(f, a, b, x_centers, areas, endpoints, cross_section)
        
        print("Generating 3D visualization...")
        fig_3d = plot_3d(f, a, b, n, cross_section)
        
        # Show all plots
        print("\nDisplaying plots...")
        plt.show()
        
    except ValueError as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nPlease run the program again and ensure all inputs are valid.")
        return
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        return
    
    print("\n✓ Program completed successfully!")


if __name__ == "__main__":
    main()
