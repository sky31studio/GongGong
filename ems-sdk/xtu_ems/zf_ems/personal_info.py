import bs4

from xtu_ems.common.exception import SessionInvalidException
from xtu_ems.common.model import StudentBasicInfo
from xtu_ems.common.sess import HttpSessionHolder


def parse_personal_info(soup) -> StudentBasicInfo:
    """
    解析个人信息数据

    :param soup: 原始数据
    :return: 解析后的个人信息对象
    """

    basic_info_panel = soup.find(id="content_xsxxgl_xsjbxx")
    student_id = basic_info_panel.find(id="col_xh").text.strip()
    name = basic_info_panel.find(id="col_xm").text.strip()
    gender = basic_info_panel.find(id="col_xbm").text.strip()
    birthday = basic_info_panel.find(id="col_csrq").text.strip()
    entrance_day = basic_info_panel.find(id="col_rxrq").text.strip()

    # 学籍信息面板
    student_info_panel = soup.find(id="content_xsxxgl_xsxjxx")
    major = student_info_panel.find(id="col_zyh_id").text.strip()
    class_ = student_info_panel.find(id="col_bh_id").text.strip()
    college = student_info_panel.find(id="col_jg_id").text.strip()
    return StudentBasicInfo(
        student_id=student_id,
        name=name,
        gender=gender,
        birthday=birthday,
        major=major,
        class_=class_,
        entrance_day=entrance_day,
        college=college
    )


async def get_student_info(session: HttpSessionHolder) -> StudentBasicInfo:
    """
    获取个人信息

    :param session: 已登录的 HttpSessionHolder 对象
    :return: 个人信息对象
    """
    async with session.to_aiohttp_session() as http_session:
        async with http_session.get(
            "https://jw.xtu.edu.cn/jwglxt/xsxxxggl/xsgrxxwh_cxXsgrxx.html?gnmkdm=N100801&layout=default",
            allow_redirects=False
        ) as response:
            if response.status != 200:
                raise SessionInvalidException("Failed to fetch personal info page")
            text = await response.text()
            # 从返回的 HTML 中提取个人信息数据
            soup = bs4.BeautifulSoup(text, "html.parser")
            return parse_personal_info(soup)
