from pathlib import Path
from datetime import date, timedelta
import json
import os
import urllib.request

from PIL import Image, ImageDraw, ImageFont


SCRIPT_DIR = Path(__file__).resolve().parent
OUT = (SCRIPT_DIR.parent if SCRIPT_DIR.name == "scripts" else SCRIPT_DIR) / "ascii-profile.gif"
W, H = 1200, 1120
ROWS, COLS = 51, 116
X, Y, LINE = 31, 28, 21
BG, LIME, WHITE, GRAY, DIM = "#0A0A0A", "#D0FF00", "#FFFFFF", "#E5E5E5", "#707070"
FONT_PATHS = [
    "/System/Library/Fonts/Menlo.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
]
FONT = ImageFont.truetype(next(path for path in FONT_PATHS if Path(path).exists()), 16)

LOGO = [
    "#       #####  #          #",
    "#         #    #         # #",
    "#         #    #        #   #",
    "#         #    #        #####",
    "#         #    #        #   #",
    "#####   #####  #####    #   #",
]

PANELS = [
    (2, "ABOUT", ["LILA AYDIN", "PRODUCT DESIGNER / CREATIVE DEVELOPER", "ISTANBUL, TURKEY"], 18),
    (11, "CURRENT", ["MISAFIR KITABEVI", "E-COMMERCE / WEB DESIGN / DEVELOPMENT"], 40),
    (19, "LANGUAGES", ["ENGLISH / GERMAN / TURKISH"], 60),
    (26, "LINKS", ["LILADESIGN.DEV", "DRIBBBLE / INSTAGRAM / EMAIL"], 76),
]

FALLBACK_CONTRIBUTIONS = dict([
    ("2026-07-19", 1), ("2026-07-26", 3), ("2026-08-02", 4), ("2026-08-09", 2),
    ("2026-07-13", 1), ("2026-07-27", 3), ("2026-08-03", 2), ("2026-08-10", 2),
    ("2026-05-12", 1), ("2026-05-19", 4), ("2026-05-26", 1), ("2026-06-23", 1),
    ("2026-07-21", 2), ("2026-07-28", 2), ("2026-08-04", 1), ("2026-04-01", 1),
    ("2026-04-08", 1), ("2026-04-22", 1), ("2026-05-27", 1), ("2026-07-22", 1),
    ("2026-07-29", 2), ("2026-08-05", 1), ("2026-03-19", 1), ("2026-04-23", 1),
    ("2026-05-21", 1), ("2026-07-30", 1), ("2026-08-06", 1), ("2026-03-20", 1),
    ("2026-04-17", 1), ("2026-04-24", 1), ("2026-05-01", 1), ("2026-07-24", 1),
    ("2026-07-31", 4), ("2026-08-07", 1), ("2026-04-04", 1), ("2026-04-25", 1),
    ("2026-07-25", 2), ("2026-08-01", 2),
])


def load_contributions() -> tuple[dict[str, int], int, str]:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        return FALLBACK_CONTRIBUTIONS, 266, "2026-08-10"

    today = date.today()
    start = today - timedelta(days=365)
    query = """
    query($login: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $login) {
        contributionsCollection(from: $from, to: $to) {
          contributionCalendar {
            totalContributions
            weeks { contributionDays { date contributionLevel } }
          }
        }
      }
    }
    """
    levels = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
    body = json.dumps({
        "query": query,
        "variables": {
            "login": "slyim",
            "from": f"{start.isoformat()}T00:00:00Z",
            "to": f"{today.isoformat()}T23:59:59Z",
        },
    }).encode()
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        calendar = json.load(response)["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    contributions = {
        day["date"]: levels[day["contributionLevel"]]
        for week in calendar["weeks"]
        for day in week["contributionDays"]
        if day["contributionLevel"] != "NONE"
    }
    return contributions, calendar["totalContributions"], today.isoformat()


CONTRIBUTIONS, CONTRIBUTION_TOTAL, UPDATED = load_contributions()


def line_points(row1: int, col1: int, row2: int, col2: int) -> list[tuple[int, int, str]]:
    length = max(abs(row2 - row1), abs(col2 - col1))
    points = []
    for i in range(1, length + 1):
        t = i / length
        row = round(row1 + (row2 - row1) * t)
        col = round(col1 + (col2 - col1) * t)
        char = "|" if col == col1 else ("/" if (row2 - row1) * (col2 - col1) < 0 else "\\")
        if not points or points[-1][:2] != (row, col):
            points.append((row, col, char))
    return points


TREE = [(row, 27, "|") for row in range(32, 18, -1)]
TREE += line_points(26, 27, 15, 13)
TREE += line_points(24, 27, 13, 40)
TREE += line_points(22, 27, 11, 21)
TREE += line_points(20, 27, 11, 33)
TREE += line_points(21, 27, 14, 8)

LEAVES = [
    (10, 21), (10, 31), (10, 36), (11, 17), (11, 24), (11, 34), (11, 41),
    (12, 12), (12, 20), (12, 28), (12, 38), (12, 44), (13, 8), (13, 16),
    (13, 25), (13, 33), (13, 41), (13, 47), (14, 5), (14, 12), (14, 21),
    (14, 30), (14, 37), (14, 45), (15, 8), (15, 18), (15, 27), (15, 35),
    (15, 43), (16, 12), (16, 22), (16, 31), (16, 40), (17, 16), (17, 26),
    (17, 36), (18, 10), (18, 20), (18, 32), (18, 44), (19, 15), (19, 38),
]

GEMS = [(21, 5), (23, 45), (27, 11), (28, 40)]


def make_frame(step: int) -> Image.Image:
    chars = [[" " for _ in range(COLS)] for _ in range(ROWS)]
    colors = [[GRAY for _ in range(COLS)] for _ in range(ROWS)]

    def put(row: int, col: int, value: str, color: str = GRAY) -> None:
        for offset, char in enumerate(value):
            target = col + offset
            if 0 <= row < ROWS and 0 <= target < COLS:
                chars[row][target], colors[row][target] = char, color

    border = min(COLS - 2, step * 8)
    put(0, 0, "+" + "-" * border, LIME)
    put(ROWS - 1, 0, "+" + "-" * border, LIME)
    if border == COLS - 2:
        put(0, COLS - 1, "+", LIME)
        put(ROWS - 1, COLS - 1, "+", LIME)
    for row in range(1, ROWS - 1):
        put(row, 0, "|", LIME)
        put(row, COLS - 1, "|", LIME)

    logo_count = max(0, (step - 4) * 10)
    used = 0
    for row, logo_row in enumerate(LOGO, 2):
        visible = logo_row[: max(0, logo_count - used)]
        put(row, 4, visible, WHITE)
        used += len(logo_row)
    put(9, 4, "PRODUCT DESIGN / CREATIVE DEVELOPMENT"[: max(0, step - 8)], GRAY)

    tree_count = max(0, min(len(TREE), (step - 10) * 2))
    for row, col, char in TREE[:tree_count]:
        put(row, col, char, LIME)

    leaf_count = max(0, min(len(LEAVES), step - 42))
    leaf_chars = (".", "o", "*", "+")
    for index, (row, col) in enumerate(LEAVES[:leaf_count]):
        breeze = 1 if step > 88 and (step + index) % 16 == 0 else 0
        put(row, min(COLS - 2, col + breeze), leaf_chars[(step // 4 + index) % len(leaf_chars)], LIME)

    for index, (row, col) in enumerate(GEMS):
        if step < 64 + index * 5:
            continue
        shimmer = step > 96 and (step + index * 3) % 12 < 3
        put(row, col + 1, "/\\", WHITE if shimmer else LIME)
        put(row + 1, col, "<##>", LIME if shimmer else WHITE)
        put(row + 2, col + 1, "\\/", WHITE if shimmer else LIME)
        if shimmer:
            put(row, col - 2, "*", LIME)
            put(row + 1, col + 5, "+", LIME)

    grass_count = max(0, min(COLS - 2, (step - 50) * 3))
    grass = "'.^.," * ((COLS // 5) + 1)
    start = max(1, 27 - grass_count // 2)
    end = min(COLS - 1, 28 + (grass_count + 1) // 2)
    put(33, start, grass[: end - start], LIME)

    panel_col, panel_width = 55, 56
    for top, title, body, start_step in PANELS:
        lines = [
            "+ " + title + " " + "+" * max(1, panel_width - len(title) - 4),
            *["| " + line for line in body],
            "+" * panel_width,
        ]
        stream = "\n".join(line.ljust(panel_width) for line in lines)
        reveal = max(0, (step - start_step) * 11)
        shown = stream[:reveal]
        for offset, line in enumerate(shown.split("\n")):
            color = LIME if offset in (0, len(lines) - 1) else WHITE
            put(top + offset, panel_col, line, color)

    contribution_top = 36
    contribution_width = COLS - 8
    contribution_lines = [
        f"+ CONTRIBUTIONS / {CONTRIBUTION_TOTAL} IN THE LAST YEAR " + "+" * 68,
        f"| UPDATED {UPDATED}",
        "+" * contribution_width,
    ]
    header_reveal = max(0, (step - 78) * 14)
    header_stream = "\n".join(line[:contribution_width].ljust(contribution_width) for line in contribution_lines)
    for offset, line in enumerate(header_stream[:header_reveal].split("\n")):
        put(contribution_top + offset, 4, line, LIME if offset in (0, 2) else GRAY)

    visible_weeks = max(0, min(53, (step - 84) * 2))
    end_date = date.fromisoformat(UPDATED)
    start_date = end_date - timedelta(days=(end_date.weekday() + 1) % 7 + 52 * 7)
    heat_colors = [DIM, GRAY, LIME, LIME, WHITE]
    for day in range(7):
        put(contribution_top + 4 + day, 5, "|", LIME)
    for week in range(visible_weeks):
        for day in range(7):
            current = start_date.fromordinal(start_date.toordinal() + week * 7 + day)
            level = CONTRIBUTIONS.get(current.isoformat(), 0)
            char = ". " if level == 0 else "<>"
            if step > 112 and level and (week + day + step) % 13 == 0:
                char = "**"
            put(contribution_top + 4 + day, 8 + week * 2, char, heat_colors[level])
    if visible_weeks == 53:
        put(contribution_top + 11, 4, "+" * contribution_width, LIME)
        put(contribution_top + 12, 4, "LESS  .  <>  MORE", GRAY)

    if step > 92:
        scan_row = 2 + ((step - 92) % 30)
        for col in range(2, COLS - 2):
            if chars[scan_row][col] != " ":
                colors[scan_row][col] = WHITE if colors[scan_row][col] == LIME else LIME

    image = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(image)
    char_w = draw.textlength("M", font=FONT)
    for row in range(ROWS):
        for col in range(COLS):
            char = chars[row][col]
            if char != " ":
                draw.text((X + col * char_w, Y + row * LINE), char, font=FONT, fill=colors[row][col])
    return image


steps = list(range(126))
frames = [make_frame(125), *(make_frame(step) for step in steps), make_frame(125)]
durations = [1100, *([70] * len(steps)), 1100]
frames[0].save(
    OUT,
    save_all=True,
    append_images=frames[1:],
    duration=durations,
    loop=0,
    optimize=True,
    disposal=2,
)
assert OUT.exists() and OUT.stat().st_size > 10_000
print(OUT)
