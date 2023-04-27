from flask import Flask, request, render_template, jsonify
from scrape import scrape, process_pages
import async_reqs

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/results", methods=["GET"])
def results():
    master_dict = []
    # name = request.form.get("name")
    name = request.args.get("name")
    url_list = scrape(name)
    # print(url_list)
    print("Pages:", len(url_list))

    chunked_list = [
        url_list[i : i + 20] for i in range(0, len(url_list), 20)
    ]  # page_urls also need to be sent in chunks so as not to overwhelm server with requests
    for item in chunked_list:
        entries = async_reqs.receiving(item)
        master_dict.append(entries)

    return master_dict


if __name__ == "__main__":
    app.run()
