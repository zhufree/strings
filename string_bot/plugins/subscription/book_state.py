from pyquery import PyQuery as pq
import requests


async def get_book_info(bid):
    """
    获取book状态
    :param bid: bookid
    :return: 0: 连载中 1: 已完结 2: 不存在 dict: {}
    """
    url = f'http://www.jjwxc.net/onebook.php?novelid={bid}'
    req = requests.get(url)
    req.encoding = 'gb2312'  # 显示指定网页编码
    body = pq(req.text)

    # 判定是否完结 span itemprop="updataStatus"
    status = 2
    title = body('title').text()
    spans = body('span').items()
    oneboolt = body('table#oneboolt')
    table = None
    if len(list(oneboolt.items())) == 0:
        status = 2
    else:
        table = list(oneboolt.items())[0]
    for s in spans:
        if s.attr('itemprop') == 'updataStatus':
            if s.text() == '连载中':
                status = 0
            else:
                status = 1

    if table:
        trs = list(table('tr').items())
        last_chapter_tr = trs[-2]
        tds = list(last_chapter_tr('td').items())
        # print(last_chapter_tr.html())
        if tds[0].text() == "章节":
            return status, {'chapter_id': 0,
                            'chapter_title': "尚未开始连载",
                            'chapter_desc': "尚未开始连载",
                            'title': title}
        else:
            chapter_id = int(tds[0].text())
            chapter_title = tds[1].text().strip()
            chapter_desc = tds[2].text()
            return status, {'chapter_id': chapter_id,
                            'chapter_title': chapter_title,
                            'chapter_desc': chapter_desc,
                            'title': title}
    else:
        return status, None


async def get_bili_uname_by_room_id(room_id):
    url = 'https://api.live.bilibili.com/room_ex/v1/RoomNews/get'
    params = {'roomid': room_id}

    resp = requests.get(url, params)

    uname = resp.json().get('data').get('uname')

    return uname
