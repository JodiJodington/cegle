import requests, json, os, shutil, minify_html, datetime
from argparse import ArgumentParser;


parser = ArgumentParser()
parser.add_argument('-d', '--default_day', default=datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d"))
parser.add_argument('-o', '--output_dir', default="static")

args = parser.parse_args()

CEG_EPISODES_CACHE = ".ceg_episodes_cache.json"
ceg_episode_data = [None] * 4
try:
    f = open(CEG_EPISODES_CACHE, "r")
    ceg_episode_data = json.loads(f.read())
except FileNotFoundError:
    CEG_ID = 2260
    BASE_URL = "https://api.tvmaze.com"
    seasons = requests.get(f"{BASE_URL}/shows/{CEG_ID}/seasons").json();
    for s_i in range(len(seasons)):
        season = seasons[s_i];
        season_id = season["id"]
        episodes = requests.get(f"{BASE_URL}/seasons/{season_id}/episodes").json();
        season_episodes_list = [None] * len(episodes)
        for e_i in range(len(episodes)):
            season_episodes_list[e_i] = episodes[e_i]["name"]
        ceg_episode_data[s_i] = season_episodes_list
    with open(CEG_EPISODES_CACHE, "w") as f:
        f.write(json.dumps(ceg_episode_data))

template_str = ""
with open("template.html", "r") as f:
    template_str = f.read()

episodes_str = ""
for s_i in range(len(ceg_episode_data)):
    episodes_str += f'<div id="s{s_i + 1}-episodes">\n'
    for e_i in range(len(ceg_episode_data[s_i])):
        episode_name = ceg_episode_data[s_i][e_i]
        s_e_str = f"s{s_i + 1}e{e_i + 1}"
        episodes_str += f'<input type="radio" name="episode" id="{s_e_str}" value="{s_e_str}"></input>\n'
        episodes_str += f'<label for="{s_e_str}">S{s_i + 1}E{e_i + 1}: {episode_name}</label>\n'
    episodes_str += "</div>\n"


new_str = template_str.replace("INSERT_EPISODES_HERE", episodes_str)

base_dir = args.output_dir

with open("days.json") as days_file:
    days = json.loads(days_file.read())
    for day in days:
        date_path = day["date"].replace("-", "/")
        os.makedirs(f"{base_dir}/days/{date_path}/", exist_ok=True)
        for i in range(1,6):
            shutil.copy(f"images/{date_path}/{i}.jpg", f"{base_dir}/days/{date_path}/{i}.jpg")
        with open(f"{base_dir}/days/{date_path}/index.html", "w") as html_file:
            html_str = new_str.replace("INSERT_CORRECT_ANSWER_HERE", day["answer"])
            html_file.write(minify_html.minify(html_str, minify_js=True, minify_css=True))
with open(f"{base_dir}/index.html", "w") as f:
    default_date_path = args.default_day.replace("-", "/")
    redir_str = f'<!DOCTYPE html> <html> <head> <meta http-equiv="refresh" content="0; url=days/{default_date_path}/index.html" /> </head> </html>'
    f.write(minify_html.minify(redir_str))

