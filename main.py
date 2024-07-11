import http.client
import json
import requests
import os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB

# 環境変数を読み込む
APIKEY = os.getenv("APIKEY")
APIHOST = os.getenv("APIHOST")

if not type(APIKEY) is str or not type(APIHOST) is str:
    print("APIKEYまたはAPIHOSTが正しく設定されていません")
    exit()

conn = http.client.HTTPSConnection(APIHOST)

headers = {
    "x-rapidapi-key": APIKEY,
    "x-rapidapi-host": APIHOST,
}

# 入力で求める
songID = input("URLまたはIDを入力してください: ")

if "https" in songID:
    songID = songID.split("/")[-1].split("?")[0]

conn.request("GET", f"/downloadSong?songId={songID}", headers=headers)

res = conn.getresponse()
data = res.read()

print("APIからデータを取得しました。ファイルを取得しています...")

response = json.loads(data.decode("utf-8"))

if not response["success"]:
    print("API制限なので24時間後に再度お試しください。50/日らしいです。")
    exit()

cover = response["data"]["cover"]
downloadLink = response["data"]["downloadLink"]

title = response["data"]["title"]
artist = response["data"]["artist"]
album = response["data"]["album"]

if not title or not artist or not album or not cover or not downloadLink:
    print("メタデータが取得できませんでした")
    exit()

# ダウンロード
request1 = requests.get(downloadLink)
with open("temp.mp3", "wb") as f:
    f.write(request1.content)

request2 = requests.get(cover)
with open("temp.jpg", "wb") as f:
    f.write(request2.content)

print("ファイルの取得が完了しました。メタデータの更新を行っています...")

# メタデータの上書き
audio = MP3("temp.mp3", ID3=ID3)

audio.tags.add(
    APIC(
        encoding=3,
        mime="image/jpeg",
        type=3,
        desc="Cover",
        data=open("temp.jpg", "rb").read(),
    )
)

audio.tags.add(TIT2(encoding=3, text=title))
audio.tags.add(TPE1(encoding=3, text=artist))
audio.tags.add(TALB(encoding=3, text=album))
audio.save()

# ファイル名の変更
os.rename("temp.mp3", f"{title}.mp3")

# 一時ファイルの削除
os.remove("temp.jpg")

print("作業が完了しました")
