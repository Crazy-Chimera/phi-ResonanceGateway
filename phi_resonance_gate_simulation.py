"""
Φ‑Resonance Gate – Kuramoto Model Simulation with Accelerating Amplitude
and Resonant Shock State Locking.

This is a complete, self‑contained simulation that demonstrates the
physical principles behind the Φ‑Resonance Gate.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List
from dataclasses import dataclass, field
import math


@dataclass
class SimulationResult:
    """Complete results of a Kuramoto simulation."""
    time_points: List[float] = field(default_factory=list)
    order_parameter: List[float] = field(default_factory=list)
    phases: List[np.ndarray] = field(default_factory=list)
    coupling: List[float] = field(default_factory=list)
    shock_applied: bool = False
    locked_state: bool = False
    lock_duration: float = 0.0
    final_synchronization: float = 0.0


class KuramotoAcceleratingAmplitude:
    """
    Kuramoto model with exponentially accelerating coupling strength.
    Simulates neural oscillator synchronization under Φ‑Resonance Gate protocol.
    """

    def __init__(self, n_oscillators: int = 100, dt: float = 0.01):
        self.N = n_oscillators
        self.dt = dt
        # Natural frequencies drawn from a Lorentzian distribution (standard choice)
        gamma = 0.5  # width of frequency distribution
        omega_0 = 1.0  # center frequency
        self.omega = omega_0 + gamma * np.tan((np.random.rand(self.N) - 0.5) * np.pi)
        # Initial phases randomly distributed
        self.phases = np.random.uniform(0, 2 * np.pi, self.N)

    def order_parameter(self) -> float:
        """Compute the Kuramoto order parameter r (0 = no sync, 1 = perfect sync)."""
        # r * exp(iψ) = (1/N) * Σ exp(iθ_j)
        complex_sum = np.sum(np.exp(1j * self.phases))
        r = np.abs(complex_sum) / self.N
        return r

    def step(self, coupling: float):
        """Perform one integration step with given coupling strength."""
        # Kuramoto equation: dθ_i/dt = ω_i + (K/N) * Σ_j sin(θ_j - θ_i)
        # Mean-field approximation for large N
        complex_mean = np.mean(np.exp(1j * self.phases))
        r = np.abs(complex_mean)
        psi = np.angle(complex_mean)
        # Update phases
        dtheta = self.omega - (coupling * r * np.sin(self.phases - psi))
        self.phases += dtheta * self.dt
        # Keep phases in [0, 2π)
        self.phases = self.phases % (2 * np.pi)
        return r


class PhiResonanceGateSimulation:
    """
    Complete simulation of the Φ‑Resonance Gate protocol.
    Runs three phases: baseline, accelerating amplitude, resonant shock.
    """

    def __init__(self, n_oscillators: int = 100):
        self.model = KuramotoAcceleratingAmplitude(n_oscillators)

        # Simulation parameters
        self.baseline_duration = 10.0      # seconds
        self.acceleration_duration = 30.0  # seconds
        self.post_shock_duration = 40.0    # seconds

        # Baseline coupling (below critical)
        self.K_baseline = 0.3

        # Acceleration parameters
        self.K0 = 0.3                      # initial coupling for acceleration phase
        self.alpha = 0.15                  # growth rate (per second)
        self.K_critical = 1.0              # critical coupling for phase transition

        # Shock parameters
        self.shock_multiplier = 3.0        # shock amplitude multiplier
        self.shock_duration = 0.2          # seconds
        self.shock_threshold = 0.85        # order parameter threshold for shock

    def simulate(self) -> SimulationResult:
        """Run the complete simulation."""
        result = SimulationResult()
        t = 0.0

        # Phase 1: Baseline
        while t < self.baseline_duration:
            r = self.model.step(self.K_baseline)
            result.time_points.append(t)
            result.order_parameter.append(r)
            result.phases.append(self.model.phases.copy())
            result.coupling.append(self.K_baseline)
            t += self.model.dt

        # Phase 2: Accelerating amplitude
        while t < self.baseline_duration + self.acceleration_duration:
            elapsed = t - self.baseline_duration
            K = self.K0 * math.exp(self.alpha * elapsed)
            r = self.model.step(K)
            result.time_points.append(t)
            result.order_parameter.append(r)
            result.phases.append(self.model.phases.copy())
            result.coupling.append(K)
            # Check if we reached the synchronization threshold
            if r > self.shock_threshold:
                break
            t += self.model.dt

        # Phase 3: Resonant shock
        if r > self.shock_threshold:
            result.shock_applied = True
            shock_K = self.K_baseline * self.shock_multiplier
            shock_end_time = t + self.shock_duration
            while t < shock_end_time:
                r = self.model.step(shock_K)
                result.time_points.append(t)
                result.order_parameter.append(r)
                result.phases.append(self.model.phases.copy())
                result.coupling.append(shock_K)
                t += self.model.dt

        # Phase 4: Post‑shock (locked state check)
        post_shock_start = t
        while t < post_shock_start + self.post_shock_duration:
            r = self.model.step(self.K_baseline * 0.5)  # reduced coupling after shock
            result.time_points.append(t)
            result.order_parameter.append(r)
            result.phases.append(self.model.phases.copy())
            result.coupling.append(self.K_baseline * 0.5)
            t += self.model.dt

        # Analyze lock state
        if result.shock_applied:
            post_shock_r = result.order_parameter[-1]
            if post_shock_r > 0.6:
                result.locked_state = True
                result.lock_duration = self.post_shock_duration
        result.final_synchronization = result.order_parameter[-1]

        return result


def plot_results(result: SimulationResult, filename: str = "resonance_gate.png"):
    """Plot the simulation results."""
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))

    # Top: order parameter over time
    ax1 = axes[0]
    ax1.plot(result.time_points, result.order_parameter, "b-", linewidth=1)
    ax1.axhline(y=0.85, color="gold", linestyle="--", alpha=0.5, label="Shock threshold")
    ax1.axhline(y=0.6, color="green", linestyle="--", alpha=0.5, label="Lock threshold")
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Order Parameter r")
    ax1.set_title("Φ‑Resonance Gate: Synchronization Dynamics")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Middle: coupling strength over time
    ax2 = axes[1]
    ax2.plot(result.time_points, result.coupling, "r-", linewidth=1)
    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("Coupling K")
    ax2.set_title("Accelerating Amplitude and Resonant Shock")
    ax2.grid(True, alpha=0.3)

    # Bottom: phase distribution at three snapshots
    ax3 = axes[2]
    if result.phases:
        # Early
        indices = [0, len(result.phases) // 2, -1]
        colors = ["blue", "orange", "gold"]
        labels = ["Early", "At shock", "Post shock"]
        for idx, color, label in zip(indices, colors, labels):
            phases = result.phases[idx]
            ax3.hist(phases % (2 * np.pi), bins=50, alpha=0.5, color=color, label=label)
        ax3.set_xlabel("Phase (rad)")
        ax3.set_ylabel("Count")
        ax3.set_title("Phase Distribution Over Time")
        ax3.legend()
        ax3.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.show()
    print(f"Plot saved as {filename}")


if __name__ == "__main__":
    print("Φ‑Resonance Gate – Kuramoto Model Simulation")
    print("=" * 50)

    np.random.seed(42)  # reproducible results
    simulation = PhiResonanceGateSimulation(n_oscillators=100)
    result = simulation.simulate()

    print(f"Final synchronization: {result.final_synchronization:.3f}")
    print(f"Shock applied: {result.shock_applied}")
    print(f"Locked state achieved: {result.locked_state}")
    print(f"Lock duration: {result.lock_duration:.1f} s")
    print(f"Peak synchronization: {max(result.order_parameter):.3f}")

    plot_results(result)
