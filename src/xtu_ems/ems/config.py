"""配置类，这些配置可以被这个包下的所有代码公用，同时修改配置不影响业务逻辑"""
from xtu_ems.basic import BaseConfig


class BasicUrl(metaclass=BaseConfig):
    """基础地址"""

    XTU_EMS_BASE_URL: str = "https://jwxt.xtu.edu.cn/jsxsd"
    """湘潭大学教务系统-基础地址"""


class XTUEMSConfig(metaclass=BaseConfig):
    """湘潭大学教务系统配置"""

    XTU_EMS_BASE_URL: str = BasicUrl.XTU_EMS_BASE_URL
    """湘潭大学教务系统-基础地址"""

    XTU_EMS_LOGIN_URL: str = XTU_EMS_BASE_URL + "/xk/LoginToXk"
    """湘潭大学教务系统-登录地址"""

    XTU_EMS_SIG_URL: str = XTU_EMS_LOGIN_URL + "?flag=sess"
    """湘潭大学教务系统-登陆签名地址"""

    XTU_EMS_CAPTCHA_URL: str = XTU_EMS_BASE_URL + "/verifycode.servlet"
    """湘潭大学教务系统-验证码地址"""

    XTU_EMS_STUDENT_INFO_URL: str = XTU_EMS_BASE_URL + "/grxx/xsxx"
    """湘潭大学教务系统-学生信息地址"""

    XTU_EMS_STUDENT_COURSE_URL: str = XTU_EMS_BASE_URL + "/xskb/xskb_list.do"
    """湘潭大学教务系统-学生课表地址"""

    XTU_EMS_STUDENT_TRANSCRIPT_URL: str = XTU_EMS_BASE_URL + "/kscj/cjdy_dc"
    """湘潭大学教务系统-学生成绩单地址"""

    XTU_EMS_STUDENT_EXAM_URL: str = XTU_EMS_BASE_URL + "/xsks/xsksap_list"
    """湘潭大学教务系统-学生考试安排地址"""

    XTU_EMS_STUDENT_FREE_ROOM_URL: str = XTU_EMS_BASE_URL + "/kbxx/kxjs_query"
    """湘潭大学教务系统-空闲教室地址"""

    XTU_EMS_TEACHING_WEEKS_URL: str = XTU_EMS_BASE_URL + "/jxzl/jxzl_query"
    """湘潭大学教务系统-当前学期教学周历地址"""

    XTU_EMS_CURRENT_TIME: str = "2024-2025-1"
    """湘潭大学教务系统-系统当前学期"""
