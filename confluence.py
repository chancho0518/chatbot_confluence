# 출처
# 속도
# 청킹
# 메모리
# 데이터형태
# 데이터 CI/CD
# 미국식발화X(콜론)
# 통상적 메세지X(확인하라는 메세지 추가)


import os
import jmespath

from dotenv import load_dotenv
from atlassian import Confluence

load_dotenv()

class CustomConfluence(Confluence):
    def get_all_page_content(self, page_key='TD'):
        expr = '{id: id, title:title, type: type, status: status, body: body.storage.value, link: _links.webui}'
        for x in self.get_space_content(page_key)['page']['results']:
            content = jmespath.search(expr, x)
            content['link'] = f"https://alcherainc.atlassian.net/wiki/{content['link']}"
            yield content


if __name__ == "__main__":    
    confluence = CustomConfluence(
        url='https://alcherainc.atlassian.net',
        username='cr.lee@alcherainc.com',
        password=os.getenv('ATLASSIAN_API_KEY'),
        cloud=True,
    )

    for x in confluence.get_all_page_content('TD'):
        print(x)
        # print(x['link'])