import re
import csv
import datetime
from typing import List, NamedTuple

import bs4
import requests
from requests.adapters import HTTPAdapter


s = requests.Session()
s.mount('https://', HTTPAdapter(max_retries=100))


class _Result(NamedTuple):
    system: str
    date: datetime.datetime
    platform: str
    framework: str
    score: int


def Result(system, date, platform, framework, score):
    score = int(score)
    date = datetime.datetime.strptime(date, '%b %d, %Y')
    return _Result(system, date, platform, framework, score)


def get_page(page_number: int) -> bs4.BeautifulSoup:
    url = 'https://browser.geekbench.com/ml/v0/inference'
    r = s.get(url, data={'page': page_number}, )
    return bs4.BeautifulSoup(r.content, features='html.parser')


def geekbench_results(page_number: int) -> List[_Result]:
    soup = get_page(page_number)
    class_regex = re.compile('list-col-(model|text)')
    results = []
    for entry in soup.find_all(class_='list-col-inner'):
        soup_values = entry.find_all(class_=class_regex)
        user = soup_values[1].find('a')
        if user is not None:
            user.decompose()
        result = Result(*(e.text.replace('\n', ' ').strip() for e in soup_values))
        results.append(result)
    return results


if __name__ == '__main__':
    f = open('results.csv', 'a')
    writer = csv.DictWriter(f, fieldnames=_Result._fields)
    if f.tell() == 0:
        writer.writeheader()
    try:
        for page_number in range(1, 1001):
            print(page_number)
            results = geekbench_results(page_number)
            for r in results:
                writer.writerow(r._asdict())
    except Exception as e:
        print(e)
        f.flush()
