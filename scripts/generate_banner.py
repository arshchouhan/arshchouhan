import requests
import datetime
from dateutil.relativedelta import relativedelta
from PIL import Image, ImageDraw, ImageFont
import os
import sys

# --- Configuration ---
GITHUB_USERNAME = "arshchouhan"
BIRTHDATE = datetime.datetime(2004, 6, 24) # Born on 24 June 2004
LOC_API_URL = f"https://api.codetabs.com/v1/loc?github={GITHUB_USERNAME}"
GITHUB_TOKEN = os.environ.get("GH_TOKEN") # Will be provided by GitHub Actions

# Colors (Hex)
COLORS_DARK = {
    'bg': '#0d1117',
    'key': '#58a6ff',
    'value': '#c9d1d9',
    'label': '#d29922',
    'bracket': '#8b949e',
    'dot': '#30363d',
    'host': '#3fb950',
    'white': '#ffffff',
    'card_bg': '#161b22',
    'border': '#30363d',
    'green': '#3fb950',
    'red': '#f85149',
    'yellow': '#d29922'
}

COLORS_LIGHT = {
    'bg': '#ffffff',
    'key': '#0969da',
    'value': '#24292f',
    'label': '#9a6700',
    'bracket': '#57606a',
    'dot': '#d0d7de',
    'host': '#1a7f37',
    'white': '#24292f',
    'card_bg': '#f6f8fa',
    'border': '#d0d7de',
    'green': '#1a7f37',
    'red': '#cf222e',
    'yellow': '#9a6700'
}

# --- Data Fetching ---
def fetch_github_stats():
    session = requests.Session()
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "arshchouhan-banner-generator"
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    session.headers.update(headers)

    # 1. Profile Data
    public_repos_total = 0
    followers = 0
    try:
        resp = session.get(f"https://api.github.com/users/{GITHUB_USERNAME}", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            public_repos_total = data.get("public_repos", 0)
            followers = data.get("followers", 0)
    except: pass

    # 2. Pagination for All Repos
    all_repos = []
    page = 1
    while True:
        try:
            url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos?per_page=100&page={page}"
            resp = session.get(url, timeout=12)
            if resp.status_code != 200: break
            data = resp.json()
            if not data: break
            all_repos.extend(data)
            if "next" not in resp.links: break
            page += 1
        except: break

    total_stars = 0
    total_commits = 0
    total_additions = 0
    total_deletions = 0
    contributed_count = 0
    owned_count = 0

    for r in all_repos:
        is_fork = r.get("fork")
        if is_fork:
            contributed_count += 1
        else:
            owned_count += 1
            total_stars += r.get("stargazers_count", 0)
            repo_name = r["name"]
            
            # Commit count per repo for author
            try:
                comm_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/commits?author={GITHUB_USERNAME}&per_page=1"
                comm_resp = session.get(comm_url, timeout=8)
                if comm_resp.status_code == 200:
                    if "last" in comm_resp.links:
                        last_url = comm_resp.links["last"]["url"]
                        total_commits += int(last_url.split("page=")[-1])
                    elif len(comm_resp.json()) > 0:
                        total_commits += 1
            except: pass

            # Code Frequency (Additions/Deletions)
            try:
                freq_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/stats/code_frequency"
                freq_resp = session.get(freq_url, timeout=8)
                if freq_resp.status_code == 200:
                    weeks = freq_resp.json()
                    for w in weeks:
                        total_additions += w[1]
                        total_deletions += abs(w[2])
            except: pass

    net_loc = total_additions - total_deletions
    
    return {
        "followers": followers,
        "public_repos": public_repos_total,
        "contributed": contributed_count,
        "stars": total_stars,
        "commits": total_commits,
        "loc": net_loc,
        "additions": total_additions,
        "deletions": total_deletions
    }

def get_uptime():
    now = datetime.datetime.now()
    diff = relativedelta(now, BIRTHDATE)
    return f"{diff.years} years, {diff.months} months, {diff.days} days"

# --- ASCII Art ---
# Based on the user's previous reference art
ASCII_ART = [
    "       g@M%@%%@N%Nw,,        ",
    " ,M*` | ||*%gNM=]mM%g||%N,   ",
    " p!``  ' ! |``` ```|||jhlj%w ",
    " ,@L     ,,       '''|j%M]%M ",
    "jj'` .,wp@pw,        ''''|%Wg",
    "/ { | | ]@@@@@@@@@@pp.      |||||",
    "  ' ]@@@@@@@@@@@@@@p  ,    , ",
    ", : ]%%@@@@@%%%%k%h ' * | | mkr  *",
    "  j%M`      |jkk'  ~nrn=|i  ;  ",
    "  ! jrr*^`         `~\"! L' ': !",
    "   j lp;;, ./ @@  , ;\nmy \" ,~   ",
    " i r @@ @mmHM @@@@ `^****M*,p ;",
    " | ]@@@HHH]g@M%%%%H,jmgpmb% j  ",
    " ;;%%%k%k@[,,n|:.;j%%k|k%%', [ ",
    "  H|%%k%%j%k||,;;J!!'|%ij}]@   ",
    "  \"djjmkL,\"]] [,,,wwxw;#kjk`  ",
    "   %;%km%%%%M|%%jkkii|||[      ",
    "    kjj%%kkk!||||||j|||\"       ",
    "     |jm%H@@b%%kkmk%i!!, [     ",
    "      @p|j%%%jkk|||j*``;j [    ",
    "       ]@ @@g|        ,,;j%k   ",
    "       @@@@@mgmp;,,,::;jj%%k%  ",
    "       @@@@@@@@%%kgki!|jjjj%k%@ ",
    "  ^[' %@@@HH%b%k{illljkjj%%%% ; `,",
    "=[ '  .%HH%%%%%H@gkilljjj%k%\".    'i"
]

# --- Image Generation ---
def generate_image(mode="dark"):
    stats = fetch_github_stats()
    uptime = get_uptime()
    config = COLORS_DARK if mode == "dark" else COLORS_LIGHT
    
    # Setup fonts
    font_path = "scripts/JetBrainsMono-Bold.ttf"
    if not os.path.exists(font_path):
        ascii_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    else:
        ascii_font = ImageFont.truetype(font_path, 18)
        text_font = ImageFont.truetype(font_path, 16)

    # Calculate image size
    img_width = 1100
    img_height = 650
    img = Image.new('RGB', (img_width, img_height), color=config['bg'])
    draw = ImageDraw.Draw(img)

    # Draw Card Background with Padding
    padding = 20
    card_x0, card_y0 = padding, padding
    card_x1, card_y1 = img_width - padding, img_height - padding
    
    # Draw rounded card
    draw.rounded_rectangle(
        [card_x0, card_y0, card_x1, card_y1], 
        radius=15, 
        fill=config['card_bg'], 
        outline=config['border'], 
        width=1
    )

    # Draw ASCII Art column (Inside card)
    x_offset = card_x0 + 40
    y_offset = card_y0 + 50
    line_height = 20
    
    for i, line in enumerate(ASCII_ART):
        draw.text((x_offset, y_offset + i * line_height), line, font=ascii_font, fill=config['value'])

    # Draw Information column
    text_x = card_x0 + 420
    text_y = card_y0 + 50
    
    # Header: arshchouhan with solid divider
    head_text = f"{GITHUB_USERNAME} "
    draw.text((text_x, text_y), head_text, font=text_font, fill=config['white'])
    
    panel_right_x = text_x + 580
    head_lx = text_x + draw.textlength(head_text, font=text_font)
    
    if panel_right_x > head_lx:
        dash_w = draw.textlength("─", font=text_font)
        dash_count = int((panel_right_x - head_lx) / dash_w)
        draw.text((head_lx, text_y), "─" * dash_count, font=text_font, fill=config['dot'])
    
    text_y += line_height + 5

    def draw_field(key, val):
        nonlocal text_y
        key_text = f"{key}: "
        draw.text((text_x, text_y), key_text, font=text_font, fill=config['key'])
        
        # Right boundary for the value (Narrowed for shorter dots)
        panel_right_x = text_x + 580
        val_text = str(val)
        val_width = draw.textlength(val_text, font=text_font)
        
        # Draw value right-justified
        draw.text((panel_right_x - val_width, text_y), val_text, font=text_font, fill=config['value'])
        
        # Fill with dots
        key_width = draw.textlength(key_text, font=text_font)
        dots_start_x = text_x + key_width
        dots_end_x = panel_right_x - val_width - 10
        
        if dots_end_x > dots_start_x:
            dot_w = draw.textlength(".", font=text_font)
            dot_count = int((dots_end_x - dots_start_x) / dot_w)
            draw.text((dots_start_x, text_y), "." * dot_count, font=text_font, fill=config['dot'])
            
        text_y += line_height

    def draw_separator(label):
        nonlocal text_y
        text_y += 5
        label_text = f"─ {label} "
        draw.text((text_x, text_y), label_text, font=text_font, fill=config['label'])
        
        # Solid horizontal line to match the layout
        label_width = draw.textlength(label_text, font=text_font)
        sep_start_x = text_x + label_width
        sep_end_x = panel_right_x
        
        if sep_end_x > sep_start_x:
            dash_w = draw.textlength("─", font=text_font)
            dash_count = int((sep_end_x - sep_start_x) / dash_w)
            draw.text((sep_start_x, text_y), "─" * dash_count, font=text_font, fill=config['dot'])
        text_y += line_height + 2

    # Fields
    draw_field("OS", "Windows 11, Linux (WSL), Android 15")
    draw_field("Uptime", uptime)
    draw_field("Host", "127.0.0.0//Lovely Professional University")
    draw_field("Kernel", "Distributed Systems")
    draw_field("IDE", "VS Code")
    
    text_y += 5
    draw_field("Languages.Programming", "C++, Python, JavaScript, Java, SQL")
    draw_field("Languages.Web", "React, Tailwind, JSON, MongoDB, Express")
    draw_field("Computer.Core", "OS, Networking, DSA, Cybersecurity")
    draw_field("Languages.Real", "English, Hindi, Pahadi")
    
    text_y += 5
    draw_field("Hobbies.Software", "DSA, Web Dev")
    draw_field("Hobbies.Hardware", "PC Building, Cloud Architecture")
    
    draw_separator("Contact")
    draw_field("Email.Personal", "arshchouhan004@gmail.com")
    draw_field("LinkedIn", "linkedin.com/in/arshchouhan")
    draw_field("Discord", "arsh_c")
    draw_field("Twitter", "@ArshCho85958973")
    draw_field("LeetCode", "arshchouhan004")

    draw_separator("GitHub Stats")
    
    panel_right_x = text_x + 580
    mid_x = text_x + 280

    def draw_split_stat(label1, val1_prefix, val1_main, val1_extra, label2, val2, y):
        # Left half
        draw.text((text_x, y), f"{label1}: ", font=text_font, fill=config['key'])
        lx = text_x + draw.textlength(f"{label1}: ", font=text_font)
        
        # Dots for left half
        dots_end_lx = mid_x - draw.textlength(f"{val1_prefix}{val1_main} {val1_extra}", font=text_font) - 10
        if dots_end_lx > lx:
            dots = "." * int((dots_end_lx - lx) / draw.textlength(".", font=text_font))
            draw.text((lx, y), dots, font=text_font, fill=config['dot'])
            lx = mid_x - draw.textlength(f"{val1_prefix}{val1_main} {val1_extra}", font=text_font)
        
        draw.text((lx, y), val1_prefix, font=text_font, fill=config['value'])
        lx += draw.textlength(val1_prefix, font=text_font)
        draw.text((lx, y), str(val1_main), font=text_font, fill=config['value'])
        lx += draw.textlength(str(val1_main), font=text_font)
        draw.text((lx, y), f" {val1_extra}", font=text_font, fill=config['yellow'])
        
        # Separator
        draw.text((mid_x, y), "|", font=text_font, fill=config['white'])
        
        # Right half
        rx_label = mid_x + 15
        draw.text((rx_label, y), f"{label2}: ", font=text_font, fill=config['key'])
        rx_dots_start = rx_label + draw.textlength(f"{label2}: ", font=text_font)
        
        val2_text = str(val2)
        val2_w = draw.textlength(val2_text, font=text_font)
        rx_val_start = panel_right_x - val2_w
        
        if rx_val_start > rx_dots_start:
            dots = "." * int((rx_val_start - 10 - rx_dots_start) / draw.textlength(".", font=text_font))
            draw.text((rx_dots_start, y), dots, font=text_font, fill=config['dot'])
            
        draw.text((rx_val_start, y), val2_text, font=text_font, fill=config['value'])

    # Row 1: Repos and Stars
    contrib_text = f"{{Contributed: {stats['contributed']}}}"
    draw_split_stat("Repos", "", stats['public_repos'], contrib_text, "Stars", stats['stars'], text_y)
    text_y += line_height
    
    # Row 2: Commits and Followers
    draw_split_stat("Commits", "", f"{stats['commits']:,}", "", "Followers", stats['followers'], text_y)
    text_y += line_height
    
    # Row 3: LOC
    # Lines of Code on GitHub: <total> (<added>++, <removed>--)
    loc_label = "Lines of Code on GitHub: "
    draw.text((text_x, text_y), loc_label, font=text_font, fill=config['key'])
    lx = text_x + draw.textlength(loc_label, font=text_font)
    
    # Dots for LOC
    loc_vals_text = f"{stats['loc']:,} ( {stats['additions']:,}++, {stats['deletions']:,}-- )"
    dots_end = panel_right_x - draw.textlength(loc_vals_text, font=text_font) - 10
    if dots_end > lx:
        dots = "." * int((dots_end - lx) / draw.textlength(".", font=text_font))
        draw.text((lx, text_y), dots, font=text_font, fill=config['dot'])
        lx = dots_end + 10
        
    draw.text((lx, text_y), f"{stats['loc']:,} ( ", font=text_font, fill=config['value'])
    lx += draw.textlength(f"{stats['loc']:,} ( ", font=text_font)
    
    draw.text((lx, text_y), f"{stats['additions']:,}++", font=text_font, fill=config['green'])
    lx += draw.textlength(f"{stats['additions']:,}++", font=text_font)
    
    draw.text((lx, text_y), ", ", font=text_font, fill=config['value'])
    lx += draw.textlength(", ", font=text_font)
    
    draw.text((lx, text_y), f"{stats['deletions']:,}--", font=text_font, fill=config['red'])
    lx += draw.textlength(f"{stats['deletions']:,}--", font=text_font)
    
    draw.text((lx, text_y), " )", font=text_font, fill=config['value'])
    text_y += line_height
    output_path = f"assets/banner-{mode}.png"
    os.makedirs("assets", exist_ok=True)
    img.save(output_path)
    print(f"Generated {output_path}")

if __name__ == "__main__":
    # Generate both modes
    generate_image("dark")
    generate_image("light")
