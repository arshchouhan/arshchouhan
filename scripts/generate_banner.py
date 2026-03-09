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
    'label': '#d29922', # Orange-ish for headers
    'bracket': '#8b949e',
    'dot': '#30363d',
    'host': '#3fb950', # Green for name@host
    'white': '#ffffff',
    'card_bg': '#161b22', # Slightly lighter dark for card
    'border': '#30363d'
}

COLORS_LIGHT = {
    'bg': '#ffffff',
    'key': '#0969da',
    'value': '#24292f',
    'label': '#9a6700',
    'bracket': '#57606a',
    'dot': '#d0d7de',
    'host': '#1a7f37',
    'white': '#24292f', # Using dark color for "white" in light mode for readability
    'card_bg': '#f6f8fa', # Very light grey for card
    'border': '#d0d7de'
}

# --- Data Fetching ---
def fetch_github_stats():
    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    
    # Get user info
    user_data = requests.get(f"https://api.github.com/users/{GITHUB_USERNAME}", headers=headers).json()
    followers = user_data.get("followers", 0)
    public_repos = user_data.get("public_repos", 0)

    # Get repos for stars and commits (basic approach)
    repos = requests.get(f"https://api.github.com/users/{GITHUB_USERNAME}/repos?per_page=100", headers=headers).json()
    stars = sum(repo["stargazers_count"] for repo in repos)
    
    # Commits is harder via API without exhaustive searching. 
    # For now, we'll use a placeholder or better yet, total public repos's commit count if feasible
    # but that's slow. We'll use the user's current 'Total Commits' if we had a better way, 
    # but for simplicity, let's use a rough estimate or omit if too complex.
    # Actually, let's just use placeholder 1,200 for now.
    total_commits = "1,200+" # Placeholder

    # Get LOC (Lines of Code)
    try:
        loc_data = requests.get(LOC_API_URL).json()
        total_loc = sum(item["linesOfCode"] for item in loc_data)
        loc_str = f"{total_loc:,}"
    except:
        loc_str = "Unknown"

    return {
        "followers": followers,
        "public_repos": public_repos,
        "stars": stars,
        "commits": total_commits,
        "loc": loc_str
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
    
    # Setup fonts (Using JetBrains Mono or similar)
    # Note: On GitHub Runner, we might need a specific path or download the font
    font_path = "scripts/JetBrainsMono-Bold.ttf"
    if not os.path.exists(font_path):
        # Fallback to default if font doesn't exist, but we should download it in the workflow
        print("Font not found, using default (might look bad)")
        font_size = 14
        try:
            image_font = ImageFont.truetype("arial.ttf", font_size)
        except:
            image_font = ImageFont.load_default()
    else:
        image_font = ImageFont.truetype(font_path, 14)

    # Calculate image size
    img_width = 1300
    img_height = 600
    img = Image.new('RGB', (img_width, img_height), color=config['bg'])
    draw = ImageDraw.Draw(img)

    # Draw Card Background with Padding
    padding = 10
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
    x_offset = card_x0 + 20
    y_offset = card_y0 + 30
    line_height = 20
    
    for i, line in enumerate(ASCII_ART):
        draw.text((x_offset, y_offset + i * line_height), line, font=image_font, fill=config['value'])

    # Draw Information column
    text_x = card_x0 + 380
    text_y = card_y0 + 30
    
    # Header: arshchouhan
    head_text = GITHUB_USERNAME
    draw.text((text_x, text_y), head_text, font=image_font, fill=config['white'])
    draw.text((text_x + draw.textlength(head_text, font=image_font) + 10, text_y), "-" * 80, font=image_font, fill=config['dot'])
    
    text_y += line_height + 5

    def draw_field(key, val):
        nonlocal text_y
        key_text = f"{key}: "
        draw.text((text_x, text_y), key_text, font=image_font, fill=config['key'])
        
        content_right_margin = card_x1 - 40
        val_text = str(val)
        val_width = draw.textlength(val_text, font=image_font)
        
        # Right justify the value
        val_draw_x = content_right_margin - val_width
        draw.text((val_draw_x, text_y), val_text, font=image_font, fill=config['value'])
        
        # Fill the gap with dots
        key_width = draw.textlength(key_text, font=image_font)
        dots_start_x = text_x + key_width
        dots_end_x = val_draw_x - 10
        
        if dots_end_x > dots_start_x:
            dot_w = draw.textlength(".", font=image_font)
            dot_count = int((dots_end_x - dots_start_x) / dot_w)
            draw.text((dots_start_x, text_y), "." * dot_count, font=image_font, fill=config['dot'])
            
        text_y += line_height

    def draw_separator(label):
        nonlocal text_y
        text_y += 10
        label_text = f"- {label} "
        draw.text((text_x, text_y), label_text, font=image_font, fill=config['label'])
        
        label_w = draw.textlength(label_text, font=image_font)
        sep_start_x = text_x + label_w
        sep_end_x = card_x1 - 40
        
        dash_w = draw.textlength("-", font=image_font)
        if sep_end_x > sep_start_x:
            dash_count = int((sep_end_x - sep_start_x) / dash_w)
            draw.text((sep_start_x, text_y), "-" * dash_count, font=image_font, fill=config['dot'])
        text_y += line_height + 5

    # Fields
    draw_field("OS", "Windows 11, Linux (WSL), Android 15")
    draw_field("Uptime", uptime)
    draw_field("Host", "127.0.0.0//Lovely Professional University")
    draw_field("Kernel", "Digital Explorer & Backend Enthusiast")
    draw_field("IDE", "VS Code, Cursor, Neovim")
    
    text_y += 5
    draw_field("Languages.Programming", "C++, Python, JavaScript, Java, SQL")
    draw_field("Languages.Computer", "HTML, CSS, JSON, Markdown, YAML")
    draw_field("Languages.Real", "English, Hindi, Punjabi")
    
    text_y += 5
    draw_field("Hobbies.Software", "Competitive Programming, Web Dev")
    draw_field("Hobbies.Hardware", "PC Building, Cloud Architecture")
    
    draw_separator("Contact")
    draw_field("Email.Personal", "arshchouhan004@gmail.com")
    draw_field("LinkedIn", "linkedin.com/in/arshchouhan")
    draw_field("GitHub", "github.com/arshchouhan")
    draw_field("Status", "Building Scalable Systems")

    draw_separator("GitHub Stats")
    
    # Custom Github format: Repos: 40 {Contributed: 5} | Stars: 100
    repo_line = f"Repos: {stats['public_repos']} {{Contributed: 5+}} | Stars: {stats['stars']}"
    draw.text((text_x, text_y), repo_line, font=image_font, fill=config['key'])
    text_y += line_height
    
    commit_line = f"Commits: {stats['commits']} | Followers: {stats['followers']}"
    draw.text((text_x, text_y), commit_line, font=image_font, fill=config['key'])
    text_y += line_height
    
    loc_line = f"Lines of Code on GitHub: {stats['loc']}"
    draw.text((text_x, text_y), loc_line, font=image_font, fill=config['key'])

    # Save
    output_path = f"assets/banner-{mode}.png"
    os.makedirs("assets", exist_ok=True)
    img.save(output_path)
    print(f"Generated {output_path}")

if __name__ == "__main__":
    # Generate both modes
    generate_image("dark")
    generate_image("light")
