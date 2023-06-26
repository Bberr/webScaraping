import csv
import json
import requests
import datetime
from bs4 import BeautifulSoup


def get_data(keyword, page):
    headers = {
        'content-type': 'application/json;charset=UTF-8',
        'origin': 'https://pantip.com',
        'ptauthorize': 'Basic dGVzdGVyOnRlc3Rlcg==',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    }
    json_data = {
        'keyword': keyword,
        'page': page,
        'rooms': [],
        'timebias': False,
    }
    response = requests.post(
        'https://pantip.com/api/search-service/search/getresult',
        headers=headers,
        json=json_data
    )
    print(response)
    return response.json()


def get_comment(tid, url):
    headers = {
        'authority': 'pantip.com',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'th,en;q=0.9',
        'referer': url,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    params = {
        'tid': tid
    }

    response = requests.get('https://pantip.com/forum/topic/render_comments', params=params, headers=headers)
    comment_json = response.text.replace('ï»¿', '')
    comment_json = json.loads(comment_json)

    return comment_json


def convert_time(computerTime):
    date = datetime.datetime.fromtimestamp(int(computerTime))
    return date.strftime('%Y-%m-%d %H:%M:%S')


def clean_text(text):
    text = text.replace("{{eem}}", "")
    text = text.replace("{{em}}", "")
    text = text.replace("=", "")
    text = text.replace("\n", "")
    text = text.replace("-", "")
    return text


def save_to_csv(keyword, data_list):
    workbook = open(keyword + '.csv', 'w', newline='', encoding='utf-8-sig')
    writer = csv.writer(workbook)
    writer.writerow(['type', 'title', 'detail', 'created_time', 'url'])
    for item in data_list:
        writer.writerow([item['type'], item['title'], item['detail'], item['created_time'], item['url']])
    workbook.close()


if __name__ == '__main__':
    keyword = input("keyword : ")
    data_list = []
    page = 1
    isData = True
    while True:
        print("page", page)
        try:
            json_data = get_data(keyword, page)
            if not json_data['success'] or json_data['data'] == []:
                isData = False

            print(json_data)
            for item in json_data['data']:
                data = {
                    'id': "",
                    'url': "",
                    'title': "",
                    'detail': "",
                    'created_time': "",
                    'comment_url': "",
                    'total_comment': 0,
                    'type': "topic"
                }
                try:
                    data['id'] = item['id']
                    data['url'] = item['url']
                    data['title'] = clean_text(item['title'])
                    data['detail'] = clean_text(item['detail'])
                    data['created_time'] = convert_time(item['created_time'])
                    data['total_comment'] = int(item['total_comment'])

                    if data['total_comment'] >= 1:

                        data['comment_url'] = item['comment_url']
                        data_list.append(data)
                        print(data['title'])

                        comment_json = get_comment(data['id'], data['url'])
                        for i in comment_json['comments']:
                            comment_data = {
                                'url': data['url'],
                                'title': data['title'],
                                'detail': "",
                                'created_time': "",
                                'type': "comment"
                            }

                            detail = BeautifulSoup(i['message'], 'html.parser').text
                            comment_data['detail'] = clean_text(detail)
                            if comment_data['detail'] == "":
                                continue
                            comment_data['created_time'] = convert_time(i['created_time'])
                            data_list.append(comment_data)
                except:
                    continue
            page += 1
        except:
            break
        if not isData:
            break
    save_to_csv(keyword, data_list)
