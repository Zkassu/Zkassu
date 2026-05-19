import os, json, pickle, logging, time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"
MAX_REPLIES = int(os.getenv("MAX_REPLIES_PER_DAY", 3))
VIDEO_ID = os.getenv("VIDEO_ID")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
REPLIED_FILE = "replied_ids.json"
replied = set(json.load(open(REPLIED_FILE))) if os.path.exists(REPLIED_FILE) else set()

def get_youtube():
    creds = pickle.load(open("token.pickle", "rb"))
    if not creds.valid:
        creds.refresh(Request())
        pickle.dump(creds, open("token.pickle", "wb"))
    return build("youtube", "v3", credentials=creds)

def get_comments(yt):
    return yt.commentThreads().list(
        part="snippet", videoId=VIDEO_ID, maxResults=15, order="time"
    ).execute().get("items", [])

def generate_reply(text):
    prompt = f"""You are FaithfulHearts12. Reply to this YouTube comment in 1-2 short sentences.
Tone: Prayerful, encouraging, scripture-aligned. Never promotional.
If Amharic → reply in Amharic. If English → reply in English.
If spam, theological debate, or prayer request → return exactly: [SKIP]
Comment: "{text}"
Reply:"""
    res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role":"user","content":prompt}], temperature=0.3, max_tokens=120)
    return res.choices[0].message.content.strip()

def main():
    yt = get_youtube()
    comments = get_comments(yt)
    posted = 0

    for item in comments:
        if posted >= MAX_REPLIES: break
        top = item["snippet"]["topLevelComment"]
        cid = top["id"]
        author = top["snippet"]["authorDisplayName"]
        text = top["snippet"]["textDisplay"]
        if cid in replied or not item["snippet"].get("canReply"): continue

        reply = generate_reply(text)
        if reply == "[SKIP]":
            replied.add(cid)
            continue

        if DRY_RUN:
            logging.info(f"[DRY RUN] ✅ {author}: {reply}")
        else:
            try:
                yt.comments().insert(part="snippet", body={"snippet":{"parentId":cid,"textOriginal":reply}}).execute()
                logging.info(f"[LIVE] ✅ {author}: {reply}")
            except Exception as e:
                logging.error(f"❌ Failed {author}: {e}")
                continue
        replied.add(cid)
        posted += 1
        time.sleep(10)  # Safety delay

    json.dump(list(replied), open(REPLIED_FILE, "w"))
    logging.info(f"🔹 Run complete. {posted} replies processed. DRY_RUN={DRY_RUN}")

if __name__ == "__main__":
    if not os.path.exists("token.pickle"):
        logging.error("❌ Run auth.py first to get YouTube permission.")
    elif not VIDEO_ID or VIDEO_ID == "YOUR_VIDEO_ID_HERE":
        logging.error("❌ Set VIDEO_ID in .env to a real video ID.")
    else:
        main()
