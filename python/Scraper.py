import requests
from bs4 import BeautifulSoup, NavigableString, Tag

look_out = 1
infinite = False


# läd alle möglichen seitenlinks wo einzellinks zu finden sind
def get_pagination_links_from_eu_startups():
    baselink = "https://www.eu-startups.com/category/fundin/page/"
    list_of_links = []

    i = 1
    while i < look_out + 1 or infinite:
        next_link = baselink + str(i) + "/"
        page = requests.get(next_link)
        if page.ok:
            print(next_link)
            list_of_links.append(next_link)
            i += 1
        else:
            return list_of_links

    return list_of_links


#lad die einzenen artikel eines seitenlinks
def get_news_links(link):
    page = requests.get(link)
    soup_instance = BeautifulSoup(page.content, "html.parser")
    div_container = soup_instance.find_all('h3', class_='entry-title td-module-title')
    list_of_links = []
    for single_post in div_container:
        print("found:", single_post)
        result = single_post.find('a', href=True)
        list_of_links.append(result['href'])

    return list_of_links


#titel des jeweiligen artikels laden
def get_news_title(page):
    page = requests.get(page)
    soup_instance = BeautifulSoup(page.content, 'html.parser')
    div_container = soup_instance.find_all('h1', class_='tdb-title-text')
    return div_container[0].text


#inhalt des jeweiligen artikels laden
def get_news_text(page):
    # <span class="td-post-date"><time class="entry-date updated td-module-date" datetime="2022-04-26T09:59:30+00:00">April 26, 2022</time></span>
    page = requests.get(page)
    soup_instance = BeautifulSoup(page.content, 'html.parser')
    div_container = soup_instance.find('div', class_='td-post-content')
    if div_container is None:
        return ""
    children = div_container.findChild('div', recursive=False).findChildren('p', recursive=False)
    text = ""
    for textblock in children:
        for a in textblock.childGenerator():
            if isinstance(a, NavigableString):
                text = text + a + " "
            elif isinstance(a, Tag):
                text = text + a.get_text().strip() + " "
        #seperator für einzelne absätze
        text += ":!:"
    return text


#kombinieren dieser werte zu einem dict
def load_contents():
    global infinite
    if look_out == -1:
        infinite = True
    base_link_list = get_pagination_links_from_eu_startups()
    contents = dict()
    possible_links = []
    for link in base_link_list:
        possible_links.extend(get_news_links(link))
    print("start loading contents of the sites!")
    for link in possible_links:
        contents[get_news_title(link)] = get_news_text(link)
    return contents
