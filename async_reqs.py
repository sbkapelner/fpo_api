import asyncio
import aiohttp
from bs4 import BeautifulSoup
import time


async def get_page(session, url):  # get data off page
    async with session.get(url) as r:
        return await r.text()


async def get_all(session, urls):
    tasks = []
    for url in urls:
        task = asyncio.create_task(get_page(session, url))  # coroutine
        tasks.append(task)
    results = await asyncio.gather(*tasks)
    return results


async def main(urls):
    async with aiohttp.ClientSession() as session:
        data = await get_all(session, urls)
        return data


def publication_type(pub):
    if "US" in pub:
        return "USAPP"

    elif "WO" in pub:
        return "PCT"

    else:
        return "OTHER"


def pat_no_urls(results):
    list_pat_no_urls = []
    for html in results:
        soup = BeautifulSoup(html, "html.parser")
        number_tags = soup.find_all("td", {"width": "15%"})
        number_tags = [item.text.strip() for item in number_tags]
        for tag in number_tags:
            pub_type = publication_type(tag)
            match pub_type:
                case "USAPP":
                    url = (
                        f"https://www.freepatentsonline.com/y{tag[2:6]}/{tag[6:]}.html"
                    )
                case "PCT":
                    num = tag.replace("/", "")
                    url = f"https://www.freepatentsonline.com/{num}.html"
                case "OTHER":
                    url = f"https://www.freepatentsonline.com/{tag}.html"
            list_pat_no_urls.append(url)
    # print(list_pat_no_urls)
    return list_pat_no_urls  # 50*num_pages


def getting_data(indiv_page_results):
    data_dict = {}
    for item in indiv_page_results:  # items are html responses
        soup = BeautifulSoup(item, "html.parser")
        tag = (
            soup.find_all("div", {"class": "disp_doc2"})[1]
            .text.strip()
            .split("  ")[0]
            .strip(":")
        )

        fields = [
            field.text.strip().strip("\n").strip(":")
            for field in soup.find_all("div", {"class": "disp_elm_title"})
            if field.text.strip("\n").strip() != None
        ]  # some of these tags have no text
        fields = filter(None, fields)

        values = [
            value.text.replace("\n", "").strip(":").strip().replace("  ", "")
            for value in soup.find_all("div", {"class": "disp_elm_text"})
            if value.text.strip("\n").strip() != None
        ]
        values.remove(values[1])  # ?
        values = filter(None, values)

        entry = dict(map(lambda i, j: (i, j), fields, values))
        data_dict.update({f"{tag}": entry})
        # data_dict.update({f"{tag}": {}})
        # data_dict[f"{tag}"].update({f"{field}": f"{value}"})
        # print(data_dict)

    return data_dict


"""if __name__ == "__main__":
    page_urls = [
        "https://www.freepatentsonline.com/result.html?sort=relevance&srch=top&query_txt=test&submit=&patents_us=on&patents_other=on",
        "https://www.freepatentsonline.com/result.html?p=2sort=relevance&srch=top&query_txt=test&submit=&patents_us=on&patents_other=on",
        "https://www.freepatentsonline.com/result.html?p=3sort=relevance&srch=top&query_txt=test&submit=&patents_us=on&patents_other=on",
        "https://www.freepatentsonline.com/result.html?p=4sort=relevance&srch=top&query_txt=test&submit=&patents_us=on&patents_other=on",
    ]"""


def receiving(page_urls):
    results = asyncio.run(
        main(page_urls)
    )  # manages event loop; returns each page of search results' html
    # print(results)

    urls_second_eventloop = pat_no_urls(results)
    # print(urls_second_eventloop)

    chunked_list = [
        urls_second_eventloop[i : i + 10]
        for i in range(0, len(urls_second_eventloop), 10)
    ]  # break up the urls_second_eventloop into groups of 10 and sleep for 1 second between each group

    for item in chunked_list:
        temp = []
        indiv_page_results = asyncio.run(main(item))
        # print(indiv_page_results)  # each pat_no_urls response
        x = getting_data(indiv_page_results)
        print(x)
        temp.append(x)
        time.sleep(10)
    return temp

    # x = getting_data(indiv_page_results)
    # print(x)
