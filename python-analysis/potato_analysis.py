"""
Урожай картофеля в Беларуси, сезон 2025 — аналитический кейс.

Датасет собран вручную из открытых публикаций Белстата, Минсельхозпрода
Республики Беларусь и профильных СМИ (см. SOURCES.md). Скрипт:
  1. собирает данные сезона в pandas DataFrame'ы;
  2. строит статичные графики на matplotlib (для README / презентации).

Запуск:
    pip install -r requirements.txt
    python potato_analysis.py

Результат сохраняется в ./output/ (PNG).
"""

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Данные
# ---------------------------------------------------------------------------
# Источники и даты публикаций — см. SOURCES.md. Все цифры по сельхозорганизациям
# относятся к оперативному мониторингу Минсельхозпрода (не включает частный сектор).

harvest_timeline = pd.DataFrame({
    "date": pd.to_datetime(["2025-08-27", "2025-09-19", "2025-10-06", "2025-10-24"]),
    "cumulative_kt": [33, 225, 500, 668],          # тыс. тонн, нарастающим итогом
    "yoy_delta_c_ha": [89.1, 30.4, None, None],    # прирост урожайности к 2024, ц/га
})

scope_comparison = pd.DataFrame({
    "scope": [
        "Организованный сектор\n(оперативный мониторинг)",
        "Все категории хозяйств\n(итог года, Белстат)",
    ],
    "volume_kt": [675, 3000],
})

regional_breakdown = pd.DataFrame({
    "region": ["Минская", "Могилёвская", "Брестская", "Гомельская", "Остальные области*"],
    "volume_kt": [187, 139, 132, 86, 131],
}).sort_values("volume_kt", ascending=False)

cross_crop = pd.DataFrame({
    "crop": ["Зерновые и зернобобовые", "Сахарная свёкла", "Овощи",
             "Картофель", "Рапс", "Льноволокно"],
    "gross_million_t": [9.1, 5.9, 2.7, 3.0, 0.9103, 0.0583],
    "yield_c_ha": [38.2, 538, 289, None, 20.9, 12.0],
})

# ---------------------------------------------------------------------------
# 2. Палитра
# ---------------------------------------------------------------------------
COLORS = {
    "leaf": "#5F7A45",
    "leaf_deep": "#43592F",
    "clay": "#A85A2E",
    "clay_soft": "#D9B98C",
    "ink": "#2A2018",
    "ink_soft": "#5B4E3D",
    "bg": "#EFE8D8",
    "grid": "#E0D6BF",
}

plt.rcParams.update({
    "figure.facecolor": COLORS["bg"],
    "axes.facecolor": "#FBF7EE",
    "axes.edgecolor": COLORS["ink_soft"],
    "axes.labelcolor": COLORS["ink_soft"],
    "text.color": COLORS["ink"],
    "xtick.color": COLORS["ink_soft"],
    "ytick.color": COLORS["ink_soft"],
    "grid.color": COLORS["grid"],
    "font.size": 11,
    "axes.titleweight": "bold",
})


def savefig(fig, name: str) -> None:
    path = OUTPUT_DIR / f"{name}.png"
    fig.savefig(path, dpi=160, bbox_inches="tight")
    print(f"saved {path}")


# ---------------------------------------------------------------------------
# 3.1 matplotlib — динамика уборки
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(harvest_timeline["date"], harvest_timeline["cumulative_kt"],
        marker="o", color=COLORS["leaf_deep"], linewidth=2.5, markersize=7)
ax.fill_between(harvest_timeline["date"], harvest_timeline["cumulative_kt"],
                 color=COLORS["leaf"], alpha=0.15)
ax.set_title("Ход уборки картофеля, организованный сектор, 2025")
ax.set_ylabel("тыс. тонн, нарастающим итогом")
ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
ax.set_xticks(harvest_timeline["date"])
ax.set_xticklabels(harvest_timeline["date"].dt.strftime("%d.%m.%Y"), rotation=0)
ax.grid(axis="y", linewidth=0.6)
for spine in ("top", "right"):
    ax.spines[spine].set_visible(False)
savefig(fig, "01_timeline")

# ---------------------------------------------------------------------------
# 3.2 matplotlib — охват данных (организованный сектор vs итог года)
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7, 3))
bars = ax.barh(scope_comparison["scope"], scope_comparison["volume_kt"],
               color=[COLORS["clay_soft"], COLORS["clay"]], height=0.55)
for bar, value in zip(bars, scope_comparison["volume_kt"]):
    ax.text(value + 40, bar.get_y() + bar.get_height() / 2, f"{value:,.0f} тыс. т",
            va="center", fontsize=10, color=COLORS["ink"])
ax.set_title("Организованный сектор охватывает лишь ~22% итогового сбора")
ax.set_xlabel("тыс. тонн")
ax.set_xlim(0, 3400)
for spine in ("top", "right"):
    ax.spines[spine].set_visible(False)
savefig(fig, "02_scope_comparison")

# ---------------------------------------------------------------------------
# 3.3 matplotlib — региональная разбивка
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(regional_breakdown["region"], regional_breakdown["volume_kt"],
       color=COLORS["leaf"])
ax.set_title("Сбор картофеля в сельхозорганизациях по областям, 2025")
ax.set_ylabel("тыс. тонн")
ax.tick_params(axis="x", rotation=20)
for spine in ("top", "right"):
    ax.spines[spine].set_visible(False)
savefig(fig, "03_regions")

# ---------------------------------------------------------------------------
# 3.4 matplotlib — картофель на фоне других культур
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7, 4))
order = cross_crop.sort_values("gross_million_t", ascending=True)
colors = [COLORS["clay"] if c == "Картофель" else COLORS["leaf"] for c in order["crop"]]
ax.barh(order["crop"], order["gross_million_t"], color=colors)
ax.set_title("Валовой сбор ключевых культур, 2025, млн тонн")
ax.set_xlabel("млн тонн")
for spine in ("top", "right"):
    ax.spines[spine].set_visible(False)
savefig(fig, "04_cross_crop")

plt.close("all")

print("\nГотово. Проверьте папку output/.")
