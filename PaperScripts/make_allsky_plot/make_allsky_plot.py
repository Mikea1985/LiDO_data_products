"""Plot the all sky data. Make Figure 1 for the proposal."""

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord, get_body
from astropy.time import Time
from matplotlib import cm
from matplotlib.colors import ListedColormap
from matplotlib.patches import Polygon
from numpy.typing import NDArray


def make_plane(
    ax: matplotlib.axes._axes.Axes,
    latitude: float = 0.0,
    color: str = "white",
    label: None | str = "Ecliptic",
    lw: float = 1.0,
    alpha: float = 1.0,
    dash: int = 0,
) -> None:
    # Ecliptic longitude (0° to 360°), ecliptic latitude = 0 (for the ecliptic plane)
    ecliptic_longitude = np.linspace(-180.0, 180.0, 720) * u.deg  # ecliptic longitude
    # ecliptic latitude = 0 (ecliptic plane)
    ecliptic_latitude = np.zeros_like(ecliptic_longitude) + latitude * u.deg

    # Create SkyCoord object in ecliptic coordinates
    ecliptic_coords = SkyCoord(
        lon=ecliptic_longitude,
        lat=ecliptic_latitude,
        frame="geocentrictrueecliptic",  # Use ecliptic for ecliptic, icrs for equatorial
    )

    # Transform to equatorial coordinates (RA, Dec)
    equatorial_coords = ecliptic_coords.transform_to("icrs")

    # Convert the transformed RA and Dec to radians
    ra_ecliptic_rad = equatorial_coords.ra.wrap_at(180 * u.deg).radian
    dec_ecliptic_rad = equatorial_coords.dec.radian

    # Attempt to make the line dashed:
    if dash:
        ax.plot([0], [0], "--", lw=lw, color=color, alpha=alpha, label=label)
        for k in np.arange(len(dec_ecliptic_rad) // 10):
            for j in np.arange(dash + 1):
                dec_ecliptic_rad[k * 10 - j] = np.nan
    else:
        ax.plot([0], [0], lw=lw, color=color, alpha=alpha, label=label)

    for i, ra in enumerate(ra_ecliptic_rad):
        try:
            if abs(ra_ecliptic_rad[i + 1] - ra_ecliptic_rad[i - 1]) > 1:
                ra_ecliptic_rad[i] = np.nan
        except IndexError:
            if abs(ra_ecliptic_rad[0] - ra_ecliptic_rad[i - 1]) > 1:
                ra_ecliptic_rad[i] = np.nan

    # Plot the ecliptic plane (the transformed ecliptic coordinates)
    ax.plot(-ra_ecliptic_rad, dec_ecliptic_rad, lw=lw, color=color, alpha=alpha)


def add_neptune(
    ax: matplotlib.axes._axes.Axes,
    date: str = "2020-06-01",
) -> None:
    # Get Neptune's position on date
    obs_time = Time(date)
    neptune_icrs = get_body("neptune", obs_time)

    # Convert to radians and wrap RA
    ra_nep = neptune_icrs.ra.wrap_at(180 * u.deg).radian
    dec_nep = neptune_icrs.dec.radian

    # Plot Neptune's position
    ax.plot(
        -ra_nep,
        dec_nep,
        "o",
        color="cyan",
        markeredgecolor="grey",
        markeredgewidth=0.7,
        markersize=6,
        label=f"Neptune {date}",
    )


def actual_fields() -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    tmp5 = np.genfromtxt(
        "pointings.xml",
        dtype="a20,a,i,a,i,a,f,a,a1,i,a,i,a,f,a,f,a,a",
        delimiter=[20, 1, 2, 1, 2, 1, 5, 1, 1, 2, 1, 2, 1, 4, 1, 6, 1, 5],
    )
    nf = len(tmp5) - 35  # number of frames
    print(nf)
    fname = list()
    fra = np.zeros(nf)
    fdec = fra.copy()
    for i in np.arange(nf):
        j = i + 32
        fname.append(tmp5[j][0].rstrip().decode())
        fra[i] = 15 * (tmp5[j][2] + (tmp5[j][4] + tmp5[j][6] / 60.0) / 60.0)
        fdec[i] = int(tmp5[j][8].astype(str) + "1") * (
            tmp5[j][9] + (tmp5[j][11] + tmp5[j][13] / 60.0) / 60.0
        )
    fdec += (15 + 7.5) / 3600
    print(fra)
    print(type(fra))
    return fra, fdec


def plot_megacam(ax3: matplotlib.axes._axes.Axes) -> None:
    fra, fdec = actual_fields()
    fra = (fra + 180) % 360 - 180
    print(fra)
    print(fdec)
    nf = len(fra)
    # Set up dimensions of field-of-view and of individual ccd's
    dimf = np.array([3514.60, 3580.55])  # dimensions of fow, width, height "
    dimc = np.array([376.77, 850.01])  # dimensions of a chip, "
    fw = dimf[0] / 3600.0  # field width
    fh = dimf[1] / 3600.0  # Field height
    cw = dimc[0] / 3600.0  # Chip width
    ch = dimc[1] / 3600.0  # Chip height
    sgap = (fw - 9 * cw) / 8.0  # dimension small gaps, deg
    cldec = fdec - fh / 2.0  # Lower edge's Dec
    cudec = fdec + fh / 2.0  # Upper edge's Dec
    cwura = fra - (fw / 2.0) / np.cos(np.radians(cudec))  # Western upper corner's RA
    cwlra = fra - (fw / 2.0) / np.cos(np.radians(cldec))  # Western lower corner's RA
    ceura = fra + (fw / 2.0) / np.cos(np.radians(cudec))  # Eastern upper corner's RA
    celra = fra + (fw / 2.0) / np.cos(np.radians(cldec))  # Eastern lower corner's RA
    earudec = fdec + ch + sgap / 2.0
    earldec = fdec - (ch + sgap / 2.0)
    wewura = fra - (fw / 2.0 + sgap + cw) / np.cos(
        np.radians(earudec)
    )  # Western ears's western upper corner's RA
    wewlra = fra - (fw / 2.0 + sgap + cw) / np.cos(
        np.radians(earldec)
    )  # Western ears's western lower corner's RA
    weeura = fra - (fw / 2.0) / np.cos(
        np.radians(earudec)
    )  # Western ear's eastern upper corner's RA
    weelra = fra - (fw / 2.0) / np.cos(
        np.radians(earldec)
    )  # Western ear's eastern lower corner's RA
    eewura = fra + (fw / 2.0) / np.cos(
        np.radians(earudec)
    )  # Eastern ears's western upper corner's RA
    eewlra = fra + (fw / 2.0) / np.cos(
        np.radians(earldec)
    )  # Eastern ears's western lower corner's RA
    eeeura = fra + (fw / 2.0 + sgap + cw) / np.cos(
        np.radians(earudec)
    )  # Eastern ear's eastern upper corner's RA
    eeelra = fra + (fw / 2.0 + sgap + cw) / np.cos(
        np.radians(earldec)
    )  # Eastern ear's eastern lower corner's RA

    fields = [
        Polygon(
            xy=np.radians(
                [
                    [-ceura[i], cudec[i]],
                    [-cwura[i], cudec[i]],
                    [-weeura[i], earudec[i]],
                    [-wewura[i], earudec[i]],
                    [-wewlra[i], earldec[i]],
                    [-weelra[i], earldec[i]],
                    [-cwlra[i], cldec[i]],
                    [-celra[i], cldec[i]],
                    [-eewlra[i], earldec[i]],
                    [-eeelra[i], earldec[i]],
                    [-eeeura[i], earudec[i]],
                    [-eewura[i], earudec[i]],
                ]
            )
        )
        for i in np.arange(nf)
    ]
    print(len(fields))
    for j, i in enumerate(fields):
        ax3.add_artist(i)
        i.set_zorder(20)
        i.set_clip_box(ax3.bbox)
        i.set_alpha(1)
        i.set_facecolor("none")  # none = see-through
        i.set_facecolor("c")  # none = see-through
        i.set_edgecolor("none")
        i.set_linewidth(0.0)
        if j == 34:
            ax3.text(
                -np.radians(fra[j]),
                np.radians(fdec[j]) + 0.13,
                ha="center",
                va="center",
                s="Jun\n2021",
                color="k",
            )
        if j == 1:
            ax3.text(
                -np.radians(fra[j]),
                np.radians(fdec[j]) - 0.15,
                ha="center",
                va="center",
                s="Nov\n2020",
                color="k",
            )

    i.set_label("Observed fields")


def half_table(
    table1_name: ListedColormap | str = "Greys",
    table2_name: ListedColormap | str = "hot",
    reverse1: bool = False,
    reverse2: bool = False,
    pivot: float = 0.2,
    cmap1_min: float = 0.0,
    cmap1_max: float = 1.0,
    cmap2_min: float = 0.0,
    cmap2_max: float = 1.0,
) -> ListedColormap:
    """
    Splice together two matplotlib color tables.
    """

    n_col = 256
    cmap1 = cm.get_cmap(table1_name, n_col)
    cmap2 = cm.get_cmap(table2_name, n_col)

    pivot_int = int(round(pivot * n_col))
    pivot_int = max(pivot_int, 0)
    pivot_int = min(pivot_int, 255)
    n_cmap1 = pivot_int
    n_cmap2 = n_col - pivot_int

    # initialize
    newcolors = cmap1(np.linspace(0, 1, n_col))

    # now hack
    if reverse1:
        newcolors[:pivot_int, :] = cmap1(np.linspace(cmap1_max, cmap1_min, n_cmap1))
    else:
        newcolors[:pivot_int, :] = cmap1(np.linspace(cmap1_min, cmap1_max, n_cmap1))
    if reverse2:
        newcolors[pivot_int:, :] = cmap2(np.linspace(cmap2_max, cmap2_min, n_cmap2))
    else:
        newcolors[pivot_int:, :] = cmap2(np.linspace(cmap2_min, cmap2_max, n_cmap2))
    newcmp = ListedColormap(newcolors)

    return newcmp


try:
    ra_all, dec_all, koz = np.genfromtxt(
        "det32_nohead_-90to90.dat", usecols=(14, 15, 22), unpack=True
    )
    # Filter Kozai objects and convert RA from hours to degrees
    ra_deg = 15 * ra_all[koz.astype(bool)]
    dec = dec_all[koz.astype(bool)]
except FileNotFoundError:
    ra_hr, dec = np.genfromtxt(
        "kozai_nohead_onlycoords_-90to90.dat", usecols=(0, 1), unpack=True
    )
    ra_deg = 15 * ra_hr

# Convert RA to radians and wrap it for Hammer (centered at 180°)
ra_rad = np.radians(ra_deg)
ra_rad = np.remainder(ra_rad + 2 * np.pi, 2 * np.pi)  # Ensure range 0–2pi
ra_rad[ra_rad > np.pi] -= 2 * np.pi  # Convert to -pi to pi
dec_rad = np.radians(dec)

# Plot in Hammer projection
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection="hammer")

plasma = cm.get_cmap("plasma", 256)
newcolors = plasma(np.linspace(0, 1, 256))
print(newcolors)
newcolors0 = np.array(newcolors[0])
newcolors1 = np.array([1, 1, 1, 1])
for i, c in enumerate(newcolors):
    print(":")
    print(
        newcolors1 * i / len(newcolors)
        + newcolors0 * (len(newcolors) - i) / len(newcolors)
    )
    print(newcolors[i, :])
    newcolors[i, :] = newcolors0 * i / len(newcolors) + newcolors1 * (
        len(newcolors) - i
    ) / len(newcolors)

newcmp = ListedColormap(newcolors)

cmap = half_table(
    pivot=0.05,
    table1_name=newcmp,
    reverse1=False,
    # table1_name='Blues', reverse1=False,
    table2_name="plasma",
    reverse2=False,
    cmap1_min=0,
    cmap1_max=1,
    cmap2_min=0,
    cmap2_max=1,
)

# It seems matplotlib doesn't project everything correctly,
# So I'll have to project the coordinates into the hammer projection myself.
z = np.sqrt(1 + np.cos(dec_rad) * np.cos(ra_rad / 2))
x = -(2**1.5 * np.cos(dec_rad) * np.sin(ra_rad / 2)) / z
y = 2**0.5 * np.sin(dec_rad) / z
# Step 1: Create the hexbin with raw counts
hb = ax.hexbin(x, y, gridsize=120, cmap=cmap, mincnt=0, linewidth=0.15, rasterized=True)

# Step 2: Get the raw counts
counts = hb.get_array()  # This is the count in each hexbin
max_count = counts.max()

# Step 3: Normalize counts (now density from 0 to 1)
normalized_counts = counts / max_count
hb.set_array(normalized_counts)

# Step 4: Fix the color limits and colorbar
hb.set_clim(0, 1)  # ensures colormap uses full 0–1 range

cb = fig.colorbar(hb, orientation="horizontal", fraction=0.056, pad=0.10)
cb.set_label("Relative Density")

# Add grid lines
ax.grid(True, color="gray", linestyle="--", linewidth=0.5)
# Custom RA tick labels shifted from the center
tick_labels = ["14h", "16h", "18h", "20h", "22h", "0h", "2h", "4h", "6h", "8h", "10h"]
tick_locs = np.radians(
    np.linspace(150, -150, len(tick_labels))
)  # Adjusted RA ticks in radians
ax.set_xticks(tick_locs)
ax.set_xticklabels([])
# Use ax.text to place each RA label manually with a vertical shift
for i, label in enumerate(tick_labels):
    ax.text(tick_locs[i], np.radians(50), label, ha="center", va="center")
# Title and adjustments to avoid clash with labels
ax.set_title("All-Sky Density of Kozai Plutinos (Hammer Projection)", pad=20)

# Add ecliptic, etc. This stuff gets projected correctly!
make_plane(ax, latitude=0, color="black")
make_plane(ax, latitude=15, color="k", lw=1, dash=5, alpha=1, label=r"$\pm15^\circ$")
make_plane(ax, latitude=-15, color="k", lw=1, dash=5, alpha=1, label=None)

# Add Neptune
add_neptune(ax, "2020-11-09")


plot_megacam(ax)


plt.legend(
    loc="lower center",  # Place legend at the bottom left
    bbox_to_anchor=(0.5, -0.14),  # Shift it below the plot (x=0.5 is centered)
    ncol=4,  # Number of columns
    framealpha=1,
    frameon=True,
)


# Adjust the spacing for the plot to prevent title/labels clash
plt.subplots_adjust(top=0.85)
plt.savefig("../../PaperProducts/all_sky_kozai_plutino_density_hammer.png", dpi=300, bbox_inches="tight")
plt.savefig("../../PaperProducts/all_sky_kozai_plutino_density_hammer.pdf", dpi=600, bbox_inches="tight")
plt.show()

# End
