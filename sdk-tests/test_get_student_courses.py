from unittest import TestCase
from unittest.async_case import IsolatedAsyncioTestCase

from common_data import session
from xtu_ems.ems.handler import SessionInvalidException
from xtu_ems.ems.handler.get_student_courses import StudentCourseGetter
from xtu_ems.ems.model import CourseList
from xtu_ems.ems.session import Session


class TestStudentCourseGetter(TestCase):
    def test_handler(self):
        """测试获取学生课程"""
        handler = StudentCourseGetter()
        resp = handler.handler(session)
        print(resp.model_dump_json(indent=4))
        self.assertIsNotNone(resp)

    def test_extra_student_courses(self):
        """测试解析课程"""
        handler = StudentCourseGetter()
        with open('course_page.html') as f:
            resp = f.read()
        import bs4
        li = handler._extra_info(bs4.BeautifulSoup(resp, "html.parser"))
        with open('course_result.json') as f:
            expected_course_list = CourseList.model_validate_json(f.read())
            self.assertEqual(li, expected_course_list)

    def test_handler_with_invalid_session(self):
        """测试无效的session"""
        handler = StudentCourseGetter()
        with self.assertRaises(SessionInvalidException):
            handler.handler(Session(token="invalid_token"))


class TestAsyncStudentCourseGetter(IsolatedAsyncioTestCase):

    async def test_async_handler(self):
        """测试异步获取学生课程"""
        handler = StudentCourseGetter()
        resp = await handler.async_handler(session)
        print(resp.model_dump_json(indent=4))
        self.assertIsNotNone(resp)

    async def test_async_handler_with_invalid_session(self):
        """测试异步无效的session"""
        handler = StudentCourseGetter()
        with self.assertRaises(SessionInvalidException):
            await handler.async_handler(Session(token="invalid_token"))
