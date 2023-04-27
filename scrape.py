import urllib.parse
import requests
from bs4 import BeautifulSoup


def num_pages(url):
    my_headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
        "Accept-Encoding": "gzip, deflate",
        "Accept": "*/*",
        "Connection": "keep-alive",
    }

    html = requests.get(
        url, headers=my_headers
    ).text  # leave this its just to get number of pages of search results
    soup = BeautifulSoup(html, "html.parser")
    hits = soup.find("input", {"id": "hits"}).get("value")
    pages = round(int(hits) / 50)
    return pages


def build_url(query):
    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://www.freepatentsonline.com/result.html?sort=relevance&srch=top&query_txt={encoded_query}&submit=&patents_us=on&patents_other=on"
    return url, encoded_query


def pagination(pages, encoded_query):
    url = f"https://www.freepatentsonline.com/result.html?p={pages}sort=relevance&srch=top&query_txt={encoded_query}&submit=&patents_us=on&patents_other=on"
    return url


def scrape(query):
    urls = []
    url, encoded_query = build_url(query)
    urls.append(url)
    pages = num_pages(url)
    if pages > 200:
        n = 2  # THIS HAS BEEN CHNAGED FROM PAGES TO 2 FOR TESTING
    else:
        n = 2  # THIS HAS BEEN CHNAGED FROM PAGES TO 2 FOR TESTING
    for i in range(2, n + 1):
        next_url = pagination(i, encoded_query)
        urls.append(next_url)
    return urls


def publication_type(pub):
    if "US" in pub:
        return "USAPP"

    elif "WO" in pub:
        return "PCT"

    else:
        return "OTHER"


def process_pages(page_url):
    data_dict = {}
    html = requests.get(page_url).text
    soup = BeautifulSoup(html, "html.parser")
    number_tags = soup.find_all("td", {"width": "15%"})
    number_tags = [item.text.strip() for item in number_tags]
    for tag in number_tags:
        pub_type = publication_type(tag)
        match pub_type:
            case "USAPP":
                url = f"https://www.freepatentsonline.com/y{tag[2:6]}/{tag[6:]}.html"
            case "PCT":
                num = tag.replace("/", "")
                url = f"https://www.freepatentsonline.com/{num}.html"
            case "OTHER":
                url = f"https://www.freepatentsonline.com/{tag}.html"

        html = requests.get(url).text
        soup = BeautifulSoup(html, "html.parser")
        data = soup.find_all("div", {"class": "disp_doc2"})
        # print(data)
        for item in data:
            if item.find("div", {"class": "disp_elm_title"}) != None:
                field = item.find("div", {"class": "disp_elm_title"}).text.strip()
            else:
                field = "NA"
            if item.find("div", {"class": "disp_elm_text"}) != None:
                value = item.find("div", {"class": "disp_elm_text"}).text.strip()
            else:
                value = "NA"

            data_dict.update({f"{tag}": {}})
            data_dict[f"{tag}"].update({f"{field}": f"{value}"})
            # print(data_dict)

    return data_dict
