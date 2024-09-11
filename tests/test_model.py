from unittest import TestCase


class TestCourseInfo(TestCase):
    def test_week_segments(self):
        from xtu_ems.ems import CourseInfo
        course = CourseInfo(name='算法设计与分析',
                            teacher='张三',
                            classroom='科技楼101',
                            weeks='2-5,7-10')
        self.assertTrue(2 in course)
        self.assertTrue(7 in course)
        self.assertFalse(1 in course)
