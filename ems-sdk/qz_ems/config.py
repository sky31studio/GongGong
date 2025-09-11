"""配置类，这些配置可以被这个包下的所有代码公用，同时修改配置不影响业务逻辑"""

homepage_url_prefix = "http://jwxt.xtu.edu.cn/jsxsd/framework/xsMain.jsp"

app_list_url = "https://portal2020.xtu.edu.cn/api/application/applicationListByKeyAndRole"

classroom_prefix_category = {
    "北山": "北山阶梯",
    "尚美楼-": "尚美楼",
    "尚美楼": "尚美楼",
    "土木楼": "土木楼",
    "图书馆南": "图书馆南",
    "机械楼": "机械楼",
    "南山": "南山阶梯",
    "外语楼-": "外语楼",
    "文科楼-": "文科楼",
    "兴教楼A": "兴教楼A",
    "兴教楼B": "兴教楼B",
    "兴教楼C": "兴教楼C",
    "行远楼-": "行远楼",
    "一教楼-": "一教楼",
    "逸夫楼-": "逸夫楼",
    "逸夫楼": "逸夫楼",
    "兴湘学院三教-": "兴湘学院三教",
    "经管楼": "经管楼",
    "第三教学楼-": "第三教学楼",
}


class RequestConfiguration:
    """请求配置"""

    XTU_EMS_REQUEST_TIMEOUT: int = 10
    """请求超时时间"""


RequestConfig = RequestConfiguration()


class XTUEMSConfiguration:
    """湘潭大学教务系统配置"""

    XTU_EMS_BASE_URL: str = "https://jwxt.xtu.edu.cn/jsxsd"
    """湘潭大学教务系统-基础地址"""

    XTU_EMS_STUDENT_INFO_URL: str = XTU_EMS_BASE_URL + "/grxx/xsxx"
    """湘潭大学教务系统-学生信息地址"""

    XTU_EMS_STUDENT_TRANSCRIPT_URL: str = XTU_EMS_BASE_URL + "/kscj/cjdy_dc"
    """湘潭大学教务系统-学生成绩单地址"""

    XTU_EMS_STUDENT_RANK_URL: str = XTU_EMS_BASE_URL + "/kscj/cjjd_list"
    """学生排名地址"""

    XTU_EMS_STUDENT_TRANSCRIPT_MINOR_URL: str = XTU_EMS_BASE_URL + "/fxgl/fxcjdy_dc"
    """辅修成绩单地址"""

    XTU_EMS_STUDENT_EXAM_URL: str = XTU_EMS_BASE_URL + "/xsks/xsksap_list"
    """湘潭大学教务系统-学生考试安排地址"""

    XTU_EMS_STUDENT_FREE_ROOM_URL: str = XTU_EMS_BASE_URL + "/kbxx/kxjs_query"
    """湘潭大学教务系统-空闲教室地址"""

    XTU_EMS_TEACHING_WEEKS_URL: str = XTU_EMS_BASE_URL + "/jxzl/jxzl_query"
    """湘潭大学教务系统-当前学期教学周历地址"""

    """湘潭大学教务系统-session验证地址

    该部分的选择要求：

    - 当Session正常时标题不能为XTU_EMS_SESSION_VALIDATOR_TITLE
    - 请求尽可能快，否则可能会对性能造成影响
    """


XTUEMSConfig = XTUEMSConfiguration()
