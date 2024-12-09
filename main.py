import http.client
import json
import requests
import os
import shutil
from dotenv import load_dotenv
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB

load_dotenv()

# 環境変数を読み込む
APIKEY = os.getenv("APIKEY")
APIHOST = os.getenv("APIHOST")

if not type(APIKEY) is str or not type(APIHOST) is str:
    print("APIKEYまたはAPIHOSTが正しく設定されていません")
    exit()


def replace_ng_letter(text: str) -> str:
    ng_letters = ["\\", "/", ":", "*", "?", '"', "<", ">", "|"]
    ng_letters_sub = ["＼", "／", "：", "＊", "？", "”", "＜", "＞", "｜"]
    for i in range(len(ng_letters)):
        text = text.replace(ng_letters[i], ng_letters_sub[i])
    return text


def main():
    conn = http.client.HTTPSConnection(APIHOST)

    headers = {
        "x-rapidapi-key": APIKEY,
        "x-rapidapi-host": APIHOST,
    }

    # 入力で求める
    songID = input("URLまたはIDを入力してください / 最後に「zip」で圧縮 / 「del」でzipを削除: ")

    # もしこの入力が"zip"だったら、main.pyを除く全てのディレクトリをzipに圧縮して、元のファイルを消す
    if songID == "zip":
        # print("なんか壊れてる")
        # exit()

        os.system(
            "zip -r $(date +'%Y-%m-%d-%H-%M-%S').zip * -x *.py s *.zip *.nix *.toml *.lock .replit .pythonlibs .cache __pycache__ .gitignore"
        )
        # 一番下にmp3が入っている階層を対象に、すべてのファイルと階層ごと削除
        # mp3が入っていないディレクトリは削除されない
        for root, dirs, files in os.walk(".", topdown=False):
            # ディレクトリ内のすべてのファイルをチェックします
            if any(file.endswith(".mp3") for file in files):
                # mp3ファイルが見つかった場合、そのディレクトリと中身をすべて削除
                shutil.rmtree(root)
                print(f"{root}を削除しました")
            elif not os.listdir(root):
                # ディレクトリが空の場合、そのディレクトリを削除
                os.rmdir(root)
                print(f"{root}を削除しました")
        exit()
        
    if "del" in songID:
        # zipで終わるファイルのみを削除
        for file in os.listdir():
            if file.endswith(".zip"):
                os.remove(file)
                print(f"{file}を削除しました")
        exit()

    if "https" in songID:
        songID = songID.split("/")[-1].split("?")[0]
    
    print("APIからデータを取得しています...")

    conn.request("GET", f"/downloadSong?songId={songID}", headers=headers)

    res = conn.getresponse()
    data = res.read()

    print("APIからデータを取得しました。ファイルを取得しています...")

    response = json.loads(data.decode("utf-8"))

    if not response["success"]:
        print("API制限なので24時間後に再度お試しください")
        print(data.decode("utf-8"))
        exit()

    cover = response["data"]["cover"]
    downloadLink = response["data"]["downloadLink"]

    title = response["data"]["title"]
    artist = response["data"]["artist"]
    album = response["data"]["album"]

    title = replace_ng_letter(title)
    artist = replace_ng_letter(artist)
    album = replace_ng_letter(album)

    if not album:
        album = title

    if not title or not artist or not album or not cover or not downloadLink:
        print("メタデータが取得できませんでした")
        print(data.decode("utf-8"))
        exit()

    print(f"""
Info
title: {title}
artist: {artist}
album: {album}
""")

    print(f"link1 : {downloadLink}\n")
    print(f"link2 : {cover}\n")

    # request_headers = {
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    # }

    print("1/2 downloading...")

    # ダウンロード
    request1 = requests.get(downloadLink)
    with open("temp.mp3", "wb") as f:
        f.write(request1.content)

    print("2/2 downloading...")

    request2 = requests.get(cover)
    with open("temp.jpg", "wb") as f:
        f.write(request2.content)

    print("ファイルの取得が完了しました。\nメタデータの更新を行っています...")

    # メタデータの上書き
    audio = MP3("temp.mp3", ID3=ID3)

    audio.tags.add(
        APIC(
            encoding=3,
            mime="image/jpeg",
            type=3,
            desc="Cover",
            data=open("temp.jpg", "rb").read(),
        ))

    audio.tags.add(TIT2(encoding=3, text=title))
    audio.tags.add(TPE1(encoding=3, text=artist))
    audio.tags.add(TALB(encoding=3, text=album))
    audio.save()

    # ファイル名の変更
    # もしディレクトリがなかったら作る
    os.makedirs(artist, exist_ok=True)
    os.makedirs(f"{artist}/{album}", exist_ok=True)

    os.rename("temp.mp3", f"{artist}/{album}/{title}.mp3")

    # 一時ファイルの削除
    os.remove("temp.jpg")

    # zip圧縮

    print(f"{title}の作業が完了しました")


main() if __name__ == "__main__" else None
