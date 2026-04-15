"""
Memory comparison test: in_memory_solve=True vs in_memory_solve=False

This script runs the same simulation twice with different memory modes
and compares the memory footprint over fill progress.

Requires: psutil, matplotlib
    pip install psutil matplotlib
"""

import lizzy
import logging
import time
import threading
import psutil
import os
import matplotlib.pyplot as plt
import numpy as np

logging.basicConfig(level=logging.WARNING)  # Reduce log noise during test

# =============================================================================
# Memory monitoring utilities
# =============================================================================

class MemoryMonitor:
    """Monitors memory usage of the current process in a background thread."""
    
    def __init__(self, sample_interval: float = 0.1):
        self.sample_interval = sample_interval
        self.memory_samples = []  # (timestamp, memory_mb)
        self.fill_samples = []    # (timestamp, fill_fraction)
        self._running = False
        self._thread = None
        self._process = psutil.Process(os.getpid())
        self._start_time = None
        self._model = None
    
    def start(self, model=None):
        """Start monitoring memory usage."""
        self._model = model
        self._running = True
        self._start_time = time.perf_counter()
        self.memory_samples = []
        self.fill_samples = []
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
    
    def stop(self):
        """Stop monitoring and return collected samples."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
        return self.memory_samples, self.fill_samples
    
    def _monitor_loop(self):
        while self._running:
            elapsed = time.perf_counter() - self._start_time
            mem_mb = self._process.memory_info().rss / (1024 * 1024)
            self.memory_samples.append((elapsed, mem_mb))
            
            # Try to get fill progress from model
            if self._model and hasattr(self._model, '_solver') and self._model._solver:
                try:
                    solver = self._model._solver
                    total_cvs = solver.mesh.mesh_view.n_nodes
                    empty_cvs = solver.state.n_empty_cvs
                    fill_fraction = 1.0 - (empty_cvs / total_cvs) if total_cvs > 0 else 0.0
                    self.fill_samples.append((elapsed, fill_fraction))
                except:
                    pass
            
            time.sleep(self.sample_interval)


def run_simulation(in_memory_solve: bool, mesh_file: str) -> tuple:
    """
    Run a simulation with specified memory mode and monitor memory usage.
    
    Returns
    -------
    memory_samples : list of (time, memory_mb)
    fill_samples : list of (time, fill_fraction)
    solve_time : float
    peak_memory : float
    """
    print(f"\n{'='*60}")
    print(f"Running simulation with in_memory_solve={in_memory_solve}")
    print(f"{'='*60}")
    
    # Force garbage collection before starting
    import gc
    gc.collect()
    
    # Record baseline memory
    process = psutil.Process(os.getpid())
    baseline_mem = process.memory_info().rss / (1024 * 1024)
    print(f"Baseline memory: {baseline_mem:.1f} MB")
    
    # Create model
    model = lizzy.LizzyModel()
    model.read_mesh_file(mesh_file)
    model.set_simulation_parameters(
        output_interval=10, 
        in_memory_solve=in_memory_solve, 
        progress_bar=True
    )
    
    # Setup simulation
    model.create_resin("resin_01", 0.1)
    model.assign_resin("resin_01")
    
    model.create_material("domain_material", (1E-10, 1E-10, 1E-10), 0.5, 0.01)
    model.assign_material("domain_material", 'domain')
    
    model.create_pressure_inlet("inlet_left", 100000)
    model.assign_inlet("inlet_left", "left_edge")
    
    model.create_vent("vent_right", vacuum_pressure=0.0)
    model.assign_vent("vent_right", "right_edge")
    
    model.initialise_solver()
    
    # Start memory monitoring
    monitor = MemoryMonitor(sample_interval=0.05)
    monitor.start(model)
    
    # Run simulation
    start_time = time.perf_counter()
    model.solve()
    solve_time = time.perf_counter() - start_time
    
    # Save results
    result_name = f"memory_test_{'inmem' if in_memory_solve else 'streaming'}"
    model.save_results(result_name=result_name)
    
    # Stop monitoring
    memory_samples, fill_samples = monitor.stop()
    
    # Calculate peak memory (relative to baseline)
    peak_memory = max(m for _, m in memory_samples) - baseline_mem if memory_samples else 0
    final_memory = memory_samples[-1][1] - baseline_mem if memory_samples else 0
    
    print(f"Solve time: {solve_time:.2f} s")
    print(f"Peak memory (above baseline): {peak_memory:.1f} MB")
    print(f"Final memory (above baseline): {final_memory:.1f} MB")
    print(f"Results saved to: results/{result_name}/")
    
    # Cleanup
    del model
    gc.collect()
    
    return memory_samples, fill_samples, solve_time, peak_memory, baseline_mem


def interpolate_memory_vs_fill(memory_samples, fill_samples):
    """Interpolate memory values at fill progress points."""
    if not fill_samples or not memory_samples:
        return [], []
    
    mem_times = np.array([t for t, _ in memory_samples])
    mem_values = np.array([m for _, m in memory_samples])
    fill_times = np.array([t for t, _ in fill_samples])
    fill_values = np.array([f for _, f in fill_samples])
    
    # Interpolate memory at fill sample times
    mem_at_fill = np.interp(fill_times, mem_times, mem_values)
    
    return fill_values, mem_at_fill


def plot_comparison(results_inmem, results_streaming):
    """Generate comparison plots."""
    mem_inmem, fill_inmem, time_inmem, peak_inmem, base_inmem = results_inmem
    mem_stream, fill_stream, time_stream, peak_stream, base_stream = results_streaming
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot 1: Memory vs Time
    ax1 = axes[0]
    if mem_inmem:
        times_inmem = [t for t, _ in mem_inmem]
        mems_inmem = [m - base_inmem for _, m in mem_inmem]
        ax1.plot(times_inmem, mems_inmem, 'b-', label=f'in_memory=True (peak: {peak_inmem:.1f} MB)', linewidth=2)
    
    if mem_stream:
        times_stream = [t for t, _ in mem_stream]
        mems_stream = [m - base_stream for _, m in mem_stream]
        ax1.plot(times_stream, mems_stream, 'r-', label=f'in_memory=False (peak: {peak_stream:.1f} MB)', linewidth=2)
    
    ax1.set_xlabel('Time (s)', fontsize=12)
    ax1.set_ylabel('Memory above baseline (MB)', fontsize=12)
    ax1.set_title('Memory Usage vs Time', fontsize=14)
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Memory vs Fill Progress
    ax2 = axes[1]
    
    fill_vals_inmem, mem_at_fill_inmem = interpolate_memory_vs_fill(mem_inmem, fill_inmem)
    fill_vals_stream, mem_at_fill_stream = interpolate_memory_vs_fill(mem_stream, fill_stream)
    
    if len(fill_vals_inmem) > 0:
        mem_at_fill_inmem = mem_at_fill_inmem - base_inmem
        ax2.plot(fill_vals_inmem * 100, mem_at_fill_inmem, 'b-', 
                label=f'in_memory=True', linewidth=2)
    
    if len(fill_vals_stream) > 0:
        mem_at_fill_stream = mem_at_fill_stream - base_stream
        ax2.plot(fill_vals_stream * 100, mem_at_fill_stream, 'r-', 
                label=f'in_memory=False', linewidth=2)
    
    ax2.set_xlabel('Fill Progress (%)', fontsize=12)
    ax2.set_ylabel('Memory above baseline (MB)', fontsize=12)
    ax2.set_title('Memory Usage vs Fill Progress', fontsize=14)
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0, 100)
    
    plt.tight_layout()
    
    # Save figure
    output_path = 'results/memory_comparison.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\nPlot saved to: {output_path}")
    
    plt.show()


def print_summary(results_inmem, results_streaming):
    """Print summary statistics."""
    _, _, time_inmem, peak_inmem, _ = results_inmem
    _, _, time_stream, peak_stream, _ = results_streaming
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"{'Metric':<30} {'in_memory=True':>15} {'in_memory=False':>15}")
    print("-"*60)
    print(f"{'Solve time (s)':<30} {time_inmem:>15.2f} {time_stream:>15.2f}")
    print(f"{'Peak memory (MB)':<30} {peak_inmem:>15.1f} {peak_stream:>15.1f}")
    print(f"{'Memory savings':<30} {'':<15} {(1 - peak_stream/peak_inmem)*100 if peak_inmem > 0 else 0:>14.1f}%")
    print("="*60)


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    # Use a mesh with enough elements to show memory difference
    # Adjust this path to your mesh file
    MESH_FILE = "../meshes/Rect1M_R3.msh"
    
    # Check if mesh exists
    if not os.path.exists(MESH_FILE):
        print(f"Mesh file not found: {MESH_FILE}")
        print("Please update MESH_FILE path in the script.")
        exit(1)
    
    # Create results directory
    os.makedirs("results", exist_ok=True)
    
    # Run both simulations
    print("\n" + "="*60)
    print("MEMORY COMPARISON: in_memory_solve=True vs False")
    print("="*60)
    
    # Run in-memory mode first
    results_inmem = run_simulation(in_memory_solve=True, mesh_file=MESH_FILE)
    
    # Small delay between runs
    time.sleep(2)
    
    # Run streaming mode
    results_streaming = run_simulation(in_memory_solve=False, mesh_file=MESH_FILE)
    
    # Print summary
    print_summary(results_inmem, results_streaming)
    
    # Generate comparison plot
    plot_comparison(results_inmem, results_streaming)
