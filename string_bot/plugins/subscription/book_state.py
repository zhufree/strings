from pyquery import PyQuery as pq
import requests


async def get_book_info(bid):
    """
    获取book状态
    :param bid: bookid
    :return: 0: 连载中 1: 已完结 2: 房间不存在 dict: {}
    """
    url = f'http://www.jjwxc.net/onebook.php?novelid={bid}'
    req = requests.get(url)
    req.encoding = 'gb2312'  # 显示指定网页编码
    body = pq(req.text)

    # 判定是否完结 span itemprop="updataStatus"
    status = 2
    title = body('title').text()
    spans = body('span').items()
    table = list(body('table#oneboolt').items())[0]
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
