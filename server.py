import base64
import os
import re
from datetime import datetime
from io import TextIOWrapper

import markdown
from dateutil import parser
from flask import Flask, jsonify
from watchdog.events import FileCreatedEvent, FileSystemEventHandler
from watchdog.observers import polling

id = 1
articles = dict()
pattern = re.compile(
    r"^---(\r\n|\r|\n)\s*title:\s*(?P<title>.*)\s*(\r\n|\r|\n)\s*date:\s*(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})\s*(\r\n|\r|\n)---",
    flags=re.MULTILINE,
)


class ChangeHandler(FileSystemEventHandler):
    def on_created(self, event) -> None:
        if type(event) is FileCreatedEvent and str(event.src_path).endswith(".md"):
            with open(str(event.src_path), "r") as article:
                addArticle(event.src_path, article)


class Metadata:
    def __init__(self, path: str, upload_date: datetime, title: str):
        self.path = path
        self.upload_date = upload_date
        self.title = title


def addArticle(path, article: TextIOWrapper):
    article_text = article.read()
    result = re.search(
        pattern,
        article_text,
    )
    if result is None:
        return
    if result.group("date") == "" or result.group("title") == "":
        return
    title = result.group("title")
    if title in articles:
        return
    upload_date_string = result.group("date")
    upload_date = parser.parse(upload_date_string)
    metadata = Metadata(path, upload_date, title)
    articles[title] = metadata
    return


# Go through artciles and build metadata
for e in os.scandir("articles"):
    with open(e.path, "r") as article:
        addArticle(e.path, article)


observer = polling.PollingObserver()
event_handler = ChangeHandler()
observer.schedule(event_handler, "articles", recursive=False)
observer.start()


app = Flask(__name__)


@app.route("/")
def index():
    with open("index.html", "r") as index_file:
        return index_file.read()


# Gets all articles as json
@app.route("/articles")
def allArticles():
    return jsonify(
        {
            k: {**vars(v), "upload_date": v.upload_date.isoformat()}
            for k, v in articles.items()
        }
    )


@app.route("/article/<article_name>")
def getArticle(article_name: str):
    article_id = ""
    try:
        article_id = base64.urlsafe_b64decode(article_name + "==").decode()
        if article_id not in articles:
            return "Not found", 404
    except Exception as e:
        print(e)
        return "Invalid Request", 400
    print("Name: " + article_name)
    if article_id == "":
        return "Invalid Request", 400
    data = articles[article_id]
    with open(data.path, "r") as md_file:
        md_text = md_file.read()
        md_text = re.sub(pattern, "", md_text)
        rendered_md = markdown.markdown(md_text, extensions=["extra"])
        with open("articleUI.html", "r") as articleUI_file:
            articleUI_text = articleUI_file.read()
            articleUI_text = articleUI_text.replace("{{content}}", rendered_md)
            return articleUI_text
