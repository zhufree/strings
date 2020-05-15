from nonebot import CommandSession, CommandGroup

from sql_exe import sql_exe
from .live_state import *
from .book_state import *

from .push_live_info import *

__plugin_name__ = '订阅'
__plugin_usage__ = r"""订阅服务

目前仅支持: bilibili
指令: b订阅 / b取订 / b订阅列表"""

cg = CommandGroup('subscription', only_to_me=False)


@cg.command('j', aliases=['j订阅'])
async def subscription_jj(session: CommandSession):
    bid = session.get('bid', prompt='请输入你要订阅的novel id')
    group_id = session.ctx.get('group_id')

    # 检查novel是否存在
    state, book_info = await get_book_info(bid)
    if state == 2:
        session.finish('这本小说不存在')
    elif state == 1:
        session.finish('这本小说已经完结')
    # 验证是否已订阅
    sql_select = (
        'SELECT live_id FROM subscription WHERE group_id=? AND platform = "jjwxc";'
    )
    exist_sub = sql_exe(sql_select, (group_id,))

    if exist_sub:
        if (int(bid),) in exist_sub:
            session.finish('该小说已经订阅过了')

    if not group_id:
        session.finish('本功能仅支持群内订阅')

    # 订阅信息持久化
    sql = (
        'INSERT INTO subscription VALUES (NULL, ?, ?, ?);'
    )
    sql_exe(sql, (group_id, 'jjwxc', bid))

    title = book_info['title']
    chapter_id = book_info['chapter_id']
    chapter_title = book_info['chapter_title']
    chapter_desc = book_info['chapter_desc']

    await session.send(f'订阅成功:\n{title} <{bid}>\n 最新章节：{chapter_id}:{chapter_title}-{chapter_desc}')


@cg.command('bilibili_sub', aliases=['bili订阅', 'b站订阅', 'b订阅'])
async def subscription_bilibili_sub(session: CommandSession):
    bid = session.get('bid', prompt='请输入你要订阅的房间号')
    group_id = session.ctx.get('group_id')

    # 检查房间是否存在
    state, _ = await get_bili_live(bid)
    if state == 2:
        session.finish('房间不存在')

    # 验证是否已订阅
    sql_select = (
        'SELECT live_id FROM subscription WHERE group_id=?;'
    )
    exist_sub = sql_exe(sql_select, (group_id,))

    if exist_sub:
        if (int(bid),) in exist_sub:
            session.finish('该直播间已经订阅过了')

    if not group_id:
        session.finish('本功能仅支持群内订阅')

    # 订阅信息持久化
    sql = (
        'INSERT INTO subscription VALUES (NULL, ?, ?, ?);'
    )
    sql_exe(sql, (group_id, 'bilibili', bid))

    uname = await get_bili_uname_by_room_id(bid)

    await session.send(f'bilibili 订阅成功:\n{uname} <{bid}>')


@cg.command('bilibili_uns', aliases=['bili取消订阅', 'b站取消订阅', 'b取消订阅', 'b取订'])
async def subscription_bilibili_uns(session: CommandSession):
    group_id = session.ctx.get('group_id')
    bid = session.get('bid', prompt='请输入你要取消订阅的房间号')

    sql_select = (
        'SELECT live_id FROM subscription WHERE platform=? and group_id=?;'
    )
    exist_live_id = sql_exe(sql_select, ('bilibili', group_id))

    try:
        if (int(bid),) in exist_live_id:
            sql_delete = (
                'DELETE FROM subscription WHERE live_id=? AND group_id=?;'
            )
            sql_exe(sql_delete, (bid, group_id))

            uname = await get_bili_uname_by_room_id(bid)

            session.finish(f'已取消订阅: {uname}<{bid}>')
        else:
            session.finish('要取消的房间号不存在')
    except ValueError:
        session.finish('请确认输入只有房间号')


@cg.command('bilibili_list', aliases=['bili订阅列表', 'b站订阅列表', 'b订阅列表'])
async def subscription_bilibili_list(session: CommandSession):
    group_id = session.ctx.get('group_id')

    sql_select = (
        'SELECT live_id FROM subscription WHERE group_id=?;'
    )
    live_id_list = sql_exe(sql_select, (group_id,))

    if not live_id_list:
        session.finish('当前暂无订阅')

    li = []
    for lil in live_id_list:
        uname = await get_bili_uname_by_room_id(lil[0])
        form = f'{uname} <{lil[0]}>'
        li.append(form)

    await session.send('\n'.join(li))


@cg.command('jjwxc_uns', aliases=['jj取消订阅', '晋江取消订阅', 'j取消订阅', 'j取订'])
async def subscription_jjwxc_uns(session: CommandSession):
    group_id = session.ctx.get('group_id')
    bid = session.get('bid', prompt='请输入你要取消订阅的小说id')

    sql_select = (
        'SELECT live_id FROM subscription WHERE platform=? and group_id=?;'
    )
    exist_live_id = sql_exe(sql_select, ('jjwxc', group_id))

    try:
        if (int(bid),) in exist_live_id:
            sql_delete = (
                'DELETE FROM subscription WHERE live_id=? AND group_id=?;'
            )
            sql_exe(sql_delete, (bid, group_id))

            state, info = await get_book_info(bid)
            title = info['title']

            session.finish(f'已取消订阅: {title}<{bid}>')
        else:
            session.finish('要取消的小说不存在')
    except ValueError:
        session.finish('请确认输入只有小说id')


@cg.command('jjwxc_list', aliases=['jj订阅列表', '晋江订阅列表', 'j订阅列表'])
async def subscription_jjwxc_list(session: CommandSession):
    group_id = session.ctx.get('group_id')

    sql_select = (
        'SELECT live_id FROM subscription WHERE group_id=? AND platform = "jjwxc";'
    )
    live_id_list = sql_exe(sql_select, (group_id,))

    if not live_id_list:
        session.finish('当前暂无订阅')

    li = []
    for lil in live_id_list:
        state, info = await get_book_info(lil[0])
        title = info['title']
        form = f'{title} <{lil[0]}>'
        li.append(form)

    await session.send('\n'.join(li))


# bilibili订阅/取订的参数处理器
@subscription_bilibili_sub.args_parser
@subscription_bilibili_uns.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()

    if session.is_first_run:
        if stripped_arg:
            session.state['bid'] = stripped_arg.split()[0]
        return

    if not stripped_arg:
        session.pause('要取消订阅的房间号?')

    session.state[session.current_key] = stripped_arg
