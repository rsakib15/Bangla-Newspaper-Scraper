# create by Sakib Rahman on 2019-02-10
# encoding=utf8
import os
import json
from datetime import date, timedelta
from bs4 import BeautifulSoup
import requests

newspaper_base_url = 'http://www.prothom-alo.com/'
newspaper_archive_base_url = 'http://www.prothom-alo.com/archive/'

# set the starting and ending date to crawl
start_date = date(2019, 2, 11)
end_date = date(2019, 2, 11)
delta = end_date - start_date
output_dir = './data-{}-{}'.format(start_date, end_date)
output_file_name = '{}-{}.json'.format(start_date,end_date)
output_result = []

try:
    os.makedirs(output_dir)
except OSError:
    pass

print('Scraping {}'.format(newspaper_base_url))
print('Saving (image url, caption) from starting date {} to ending date {} of {}'.format(start_date, end_date, delta))

for i in range(delta.days + 1):
    date_str = start_date + timedelta(days=i)
    index = 0


    while(True):
        index = index + 1
        print ('------------------------------------------')
        print ('checking archive page: {id} and date {d}'.format(id=index, d=date_str))
        print ('------------------------------------------')

        url = newspaper_archive_base_url + str(date_str) + '?edition=all&page=' + str(index)
        archive_soup =  requests.get(url)
        soup = BeautifulSoup(archive_soup.content, "html.parser")
        all_links = soup.find_all("a", attrs={"class": "link_overlay"})
        page_links_length = len(all_links)

        if(page_links_length == 0):
            break
        else:
            for link in all_links:
                json_dict = {}
                link_separator = link.get('href').split('/')
                link = link_separator[1] + "/" +link_separator[2] + "/" + link_separator[3]
                article_url = newspaper_base_url + link
                article_data = requests.get(article_url)
                article_soup = BeautifulSoup(article_data.content, "html.parser")

                try:
                    article_info = article_soup.find_all("div", {"class": "additional_info_container"})
                    author = article_soup.find("div", {"class": "author"}).find("span", {"class": "name"}).text
                    print("Author: " + author)
                    json_dict['author'] = author
                except:
                    print("No Author")

                try:
                    date_published = article_soup.find("span", {"itemprop": "datePublished"}).text
                    json_dict['publish_date'] = date_published
                except:
                    print("No published date")

                try:
                    date_modified = article_soup.find("span", {"itemprop": "dateModified"}).text
                    json_dict['modification_date'] = date_modified
                except:
                    print("No Modification")

                try:
                    tag_array = []
                    article_tag = article_soup.find("strong", {"class": "topic_list"})
                    tags = article_soup.find("div", {"class": "topic_list"}).find_all("a")
                    for tag in tags:
                        tag_array.append(tag.text)
                    json_dict['tag'] = tag_array
                except:
                    print("No Tag Found")

                try:
                    commnent_count = article_soup.find("a", {"class": "comment_count"}).text
                    json_dict['comment_count'] =  commnent_count
                except:
                    json_dict['comment_count'] = 0

                article_content = article_soup.find_all("div", {"class": "content_detail"})
                article_title = article_soup.find("h1", {"class": "title"})
                article_body = article_soup.find("div", {"itemprop": "articleBody"})

                # print("Title:" + str(article_title.text.strip()))
                # print("URL:" + article_url.strip())
                # print("Content: " + article_body.text.strip())
                json_dict['title'] = article_title.text.strip()
                json_dict['url'] = article_url.strip()
                json_dict['article'] = article_body.text.strip()

                output_result.append(json_dict)



    with open(output_dir+ '/' + output_file_name, 'w', encoding='utf8') as outfile:
        json.dump(output_result, outfile)