"""
Photon paths around a Schwarzschild black hole (equatorial plane).

Units: G = c = 1, lengths in units of GM/c^2 (so the event horizon is at r = 2).
With u = 1/r and phi the angle around the hole, a light ray obeys

    d^2u/dphi^2 + u = 3 M u^2        (M = 1 here)

A ray coming from far away with impact parameter b starts with
    u = u0 (small),  du/dphi = sqrt(1/b^2 - u0^2 (1 - 2 M u0)).
Rays with b below b_crit = 3*sqrt(3) M are captured, rays above it escape.
"""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

M = 1.0
b_crit = 3 * np.sqrt(3) * M      # about 5.196
u0 = 1e-3                        # start far away, r0 = 1000 M


def rhs(phi, y):
    u, v = y                     # v = du/dphi
    return [v, -u + 3 * M * u**2]


def trace(b):
    """Integrate one ray. Returns phi, u(phi) and whether it was captured."""
    v0 = np.sqrt(1 / b**2 - u0**2 * (1 - 2 * M * u0))

    horizon = lambda phi, y: y[0] - 1 / (2 * M)       # u = 1/(2M) is r = 2M
    horizon.terminal = True
    escape = lambda phi, y: y[0] - (u0 + 1e-9)        # back out to r0
    escape.terminal = True
    escape.direction = -1

    sol = solve_ivp(rhs, [0, 6 * np.pi], [u0, v0], events=[horizon, escape],
                    rtol=1e-10, atol=1e-12, dense_output=True)
    phi = np.linspace(0, sol.t[-1], 2000)
    u = sol.sol(phi)[0]
    captured = len(sol.t_events[0]) > 0
    return phi, u, captured


# --- plot rays with different impact parameters ---
fig, ax = plt.subplots(figsize=(6, 6))
for b in [3.0, 4.5, 5.0, 5.2, 5.3, 6, 8, 12]:
    phi, u, captured = trace(b)
    r = 1 / u
    ax.plot(r * np.cos(phi), r * np.sin(phi), lw=1,
            color="tab:red" if captured else "tab:blue")
    print(f"b = {b:5.1f}  ->  {'captured' if captured else 'escaped'}")

ax.add_patch(plt.Circle((0, 0), 2 * M, color="k"))                    # horizon
ax.add_patch(plt.Circle((0, 0), 3 * M, fill=False, linestyle="--"))   # photon sphere
ax.set_xlim(-15, 15)
ax.set_ylim(-15, 15)
ax.set_aspect("equal")
ax.set_xlabel("x  [GM/c²]")
ax.set_ylabel("y  [GM/c²]")
ax.set_title("Photon paths around a Schwarzschild black hole")

out = Path(__file__).parent / "figures"
out.mkdir(exist_ok=True)
fig.savefig(out / "photon_paths.png", dpi=200, bbox_inches="tight")
plt.show()

# --- check: weak-field light bending should be close to 4M/b for large b ---
print("\nWeak-field deflection check")
for b in [50, 100, 200]:
    phi, u, captured = trace(b)
    deflection = phi[-1] - (np.pi - 2 * np.arcsin(b * u0))
    print(f"b = {b:4d}: simulated = {deflection:.4f}   4M/b = {4 * M / b:.4f}")
    