# Contains hidden keys values for use in other modules

PROJECT_DIR = "Lukebot/LukeBot"

VIDEO_SAVE_LOCATION = "video_website/video_website/static/videos"

with open(f"{PROJECT_DIR}/keys/filekey.key", "r") as keyfile:
    DATABASE_KEY = keyfile.read()

with open(f"{PROJECT_DIR}/keys/tenor.txt", "r") as tenorfile:
    TENOR_API_KEY = tenorfile.read()

with open(f"{PROJECT_DIR}/keys/bot_token.txt", "r") as token:
    BOT_TOKEN = token.read()

DATABASE = f"{PROJECT_DIR}/databases/database.db"
