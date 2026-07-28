"""
Figure 1 - SahaPilot System Architecture (English version)
============================================================
Recreated as an editable diagram (the original figure, extracted from
the submitted application PDF, had its labels in Turkish and baked
into a raster image with no editable source). This script reproduces
the same architecture in English using matplotlib shapes only.
============================================================
"""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


def box(ax, x, y, w, h, text, subtext=None, facecolor="#eef2ff", edgecolor="#4c51bf", fontsize=9.5):
    b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06",
                        linewidth=1.3, edgecolor=edgecolor, facecolor=facecolor)
    ax.add_patch(b)
    if subtext:
        ax.text(x + w/2, y + h*0.62, text, ha="center", va="center",
                fontsize=fontsize, fontweight="bold")
        ax.text(x + w/2, y + h*0.28, subtext, ha="center", va="center",
                fontsize=fontsize-2, color="#444444")
    else:
        ax.text(x + w/2, y + h/2, text, ha="center", va="center",
                fontsize=fontsize, fontweight="bold")


def arrow(ax, x1, y1, x2, y2, color="#555555"):
    a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=14,
                         linewidth=1.3, color=color)
    ax.add_patch(a)


fig, ax = plt.subplots(figsize=(9, 6))
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis("off")

# Top: central panel
box(ax, 2.7, 8.6, 4.6, 1.0, "Central Management Panel (Python)",
    "Fleet / map / security alerts", facecolor="#ede9fe", edgecolor="#6d28d9")

# Connector label
ax.text(5, 8.15, "MQTT / wireless", ha="center", va="center",
        fontsize=8.5, color="#666666", style="italic")

# Left column: Autonomous Vehicle - AGV
box(ax, 0.6, 7.0, 4.0, 0.7, "Autonomous Vehicle -- AGV",
    "Line following + obstacle avoidance", facecolor="#e6f4ea", edgecolor="#2f855a")
box(ax, 0.9, 5.6, 3.4, 0.9, "Sense", "IR line array + ultrasonic",
    facecolor="#f7fafc", edgecolor="#2f855a")
box(ax, 0.9, 4.2, 3.4, 0.9, "Decide", "ESP32 -- PD control + decision logic",
    facecolor="#f7fafc", edgecolor="#2f855a")
box(ax, 0.9, 2.8, 3.4, 0.9, "Act", "Motor driver + DC motors",
    facecolor="#f7fafc", edgecolor="#2f855a")

arrow(ax, 2.6, 7.0, 2.6, 6.5)
arrow(ax, 2.6, 5.6, 2.6, 5.1)
arrow(ax, 2.6, 4.2, 2.6, 3.7)

# Right column: RF Security Layer
box(ax, 5.4, 7.0, 4.0, 0.7, "RF Security Layer",
    "Wi-Fi spectrum monitoring", facecolor="#fff5f5", edgecolor="#c53030")
box(ax, 5.7, 5.6, 3.4, 0.9, "ESP32 Wi-Fi", "Promiscuous mode",
    facecolor="#f7fafc", edgecolor="#c53030")
box(ax, 5.7, 4.2, 3.4, 0.9, "Packet / OUI Analysis", "Manufacturer ID matching",
    facecolor="#f7fafc", edgecolor="#c53030")
box(ax, 5.7, 2.8, 3.4, 0.9, "Detect & Alert", "Unauthorized device / intrusion",
    facecolor="#f7fafc", edgecolor="#c53030")

arrow(ax, 7.4, 7.0, 7.4, 6.5)
arrow(ax, 7.4, 5.6, 7.4, 5.1)
arrow(ax, 7.4, 4.2, 7.4, 3.7)

# connectors from central panel down to each subsystem
arrow(ax, 4.2, 8.6, 2.6, 7.7, color="#6d28d9")
arrow(ax, 5.8, 8.6, 7.4, 7.7, color="#6d28d9")

plt.tight_layout()
plt.savefig("sekil1_sistem_mimarisi.png", dpi=160)
print("Kaydedildi: sekil1_sistem_mimarisi.png")
