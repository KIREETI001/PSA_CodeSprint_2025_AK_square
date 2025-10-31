import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("output.csv")

QC_positions = {
    "QC1": (5, 2), "QC2": (15, 2), "QC3": (25, 2), "QC4": (35, 2)
}
yard_positions = {
    "A1": (5, 12), "A2": (10, 12), "B1": (15, 12), "B2": (20, 12),
    "C1": (25, 12), "C2": (30, 12), "D1": (35, 12), "D2": (40, 12),
    "E1": (5, 10), "E2": (10, 10), "F1": (15, 10), "F2": (20, 10),
    "G1": (25, 10), "G2": (30, 10), "H1": (35, 10), "H2": (40, 10)
}

points = []
for _, row in df.iterrows():
    qc = QC_positions.get(row["QC_name"], (np.nan, np.nan))
    yd = yard_positions.get(row["assigned_yard_name"], (np.nan, np.nan))
    if np.isnan(qc[0]) or np.isnan(yd[0]):
        continue
    x = np.linspace(qc[0], yd[0], 20) + np.random.normal(0, 0.5, 20)
    y = np.linspace(qc[1], yd[1], 20) + np.random.normal(0, 0.5, 20)
    for xi, yi in zip(x, y):
        points.append((xi, yi))

pts = np.array(points)

plt.figure(figsize=(10, 6))
plt.hexbin(pts[:,0], pts[:,1], gridsize=30, cmap="plasma", mincnt=1)
plt.colorbar(label="Traffic density (HT passages)")
plt.title("Route Density Map – Optimized Planner")
plt.xlabel("X (port sector)")
plt.ylabel("Y (lane zone)")
plt.tight_layout()
plt.savefig("route_density_scatter.png", dpi=300)
print("✅ Saved route_density_scatter.png")
plt.show()
