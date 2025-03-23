import base64
import os
import dotenv

dotenv.load_dotenv()

# with open("/Users/rimo/Documents/Rimo_Studio/news_agent/app/data/icon.svg", "r") as file:
#         svg_icon = file.read()
# b64 = base64.b64encode(svg_icon.encode('utf-8')).decode('utf-8')
# svg_img_tag = f'<img src="data:image/svg+xml;base64,{b64}" width="50" height="50">'

def get_icon(icon_path, width, height):
    with open(icon_path, "r") as file:
        svg_icon = file.read()
    b64 = base64.b64encode(svg_icon.encode('utf-8')).decode('utf-8')
    svg_img_tag = f'<img src="data:image/svg+xml;base64,{b64}" width="{width}" height="{height}">'
    return svg_img_tag

width = "40"
height = "40"

APPFILEPATH = os.getenv("APPFILEPATH")
icon_dict = {
    "icon_1": get_icon(f"{APPFILEPATH}/data/icon/icon_1.svg", width, height),
    "icon_2": get_icon(f"{APPFILEPATH}/data/icon/icon_2.svg", width, height),
    "icon_3": get_icon(f"{APPFILEPATH}/data/icon/icon_3.svg", width, height),
    "icon_4": get_icon(f"{APPFILEPATH}/data/icon/icon_4.svg", width, height),
    "icon_5": get_icon(f"{APPFILEPATH}/data/icon/icon_5.svg", width, height),
    "icon_6": get_icon(f"{APPFILEPATH}/data/icon/icon_6.svg", width, height),
    "icon_7": get_icon(f"{APPFILEPATH}/data/icon/icon_7.svg", width, height),
    "icon_8": get_icon(f"{APPFILEPATH}/data/icon/icon_8.svg", width, height),
    "icon_9": get_icon(f"{APPFILEPATH}/data/icon/icon_9.svg", width, height),
    "icon_10": get_icon(f"{APPFILEPATH}/data/icon/icon_10.svg", width, height),
    "icon_11": get_icon(f"{APPFILEPATH}/data/icon/icon_11.svg", width, height),
    "icon_12": get_icon(f"{APPFILEPATH}/data/icon/icon_12.svg", width, height),
    "icon_13": get_icon(f"{APPFILEPATH}/data/icon/icon_13.svg", width, height),
    "icon_14": get_icon(f"{APPFILEPATH}/data/icon/icon_14.svg", width, height),
    "icon_15": get_icon(f"{APPFILEPATH}/data/icon/icon_15.svg", width, height),
    "icon_16": get_icon(f"{APPFILEPATH}/data/icon/icon_16.svg", width, height),
    "icon_17": get_icon(f"{APPFILEPATH}/data/icon/icon_17.svg", width, height),
    "icon_18": get_icon(f"{APPFILEPATH}/data/icon/icon_18.svg", width, height),
    "q": get_icon(f"{APPFILEPATH}/data/icon/q.svg", width, height),
}
