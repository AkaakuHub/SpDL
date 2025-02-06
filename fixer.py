import http.client
import json
import requests
import os
import shutil
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB


def replace_ng_letter(text: str) -> str:
    ng_letters = ["\\", "/", ":", "*", "?", '"', "<", ">", "|"]
    ng_letters_sub = ["＼", "／", "：", "＊", "？", "”", "＜", "＞", "｜"]
    for i in range(len(ng_letters)):
        text = text.replace(ng_letters[i], ng_letters_sub[i])
    return text


def main():
    print("メタデータを手動で書き込みます。")


    # ユーザーの入力
    title = input("曲名: ")
    artist = input("アーティスト: ")
    album = input("アルバム: ")

    title = replace_ng_letter(title)
    artist = replace_ng_letter(artist)
    album = replace_ng_letter(album)

    if not album:
        album = title

    print(f"""
Info
title: {title}
artist: {artist}
album: {album}
""")

    print("メタデータの更新を行っています...")

    # メタデータの上書き
    mp3_file_path = "temp.mp3"
    
    try:
        tags = ID3(mp3_file_path)
    except Exception:
        print("ID3タグがないため、新規作成します")
        audio = MP3(mp3_file_path, ID3=ID3)
        audio.add_tags()
        audio.save()
        tags = ID3(mp3_file_path)
        
    print("current tags:", tags)
    
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
