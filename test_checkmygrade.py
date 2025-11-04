
import unittest
from pathlib import Path
import shutil
import random
from checkmygrade import App, Student, Course


class TestCheckMyGrade(unittest.TestCase):
    def setUp(self):
        self.tmp = Path("test_workspace")
        if self.tmp.exists():
            shutil.rmtree(self.tmp)
        self.tmp.mkdir(parents=True)
        self.app = App(self.tmp)
        # seed with one course
        self.app.courses.add(Course("DATA200", "Data Science", "Intro to DS and Python"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_add_delete_update_student(self):
        s = Student("test1@example.com", "Test", "User", "DATA200", "A", 95)
        self.app.students.add(s)
        # update
        self.app.students.update("test1@example.com", marks=97, grade="A")
        found, _ = self.app.search_by_email("test1@example.com")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].marks, 97.0)
        # delete
        deleted = self.app.students.delete("test1@example.com")
        self.assertTrue(deleted)
        found2, _ = self.app.search_by_email("test1@example.com")
        self.assertEqual(len(found2), 0)

    def test_sort_and_search_timing_with_1000(self):
        # add 1000 records
        for i in range(1000):
            email = f"user{i}@example.com"
            marks = random.randint(50, 100)
            self.app.students.add(Student(email, f"FN{i}", f"LN{i}", "DATA200", "A", marks))
        # search
        _, t_search = self.app.students.search(lambda s: s.email == "user500@example.com")
        # sort by marks
        _, t_sort = self.app.sort_by_marks()
        # ensure timings are recorded (floats)
        self.assertIsInstance(t_search, float)
        self.assertIsInstance(t_sort, float)

    def test_courses_add_delete_modify(self):
        self.app.courses.add(Course("CS101", "Intro CS", "Basics"))
        self.app.courses.update("CS101", course_name="Intro to CS", description="Basics Updated")
        courses = {c.course_id: c for c in self.app.courses.list()}
        self.assertIn("CS101", courses)
        self.assertEqual(courses["CS101"].course_name, "Intro to CS")
        deleted = self.app.courses.delete("CS101")
        self.assertTrue(deleted)

    def test_auth_encrypt_decrypt(self):
        # register
        self.app.auth.register("alice@example.com", "Welcome12#_", "student")
        ok = self.app.auth.login("alice@example.com", "Welcome12#_")
        self.assertTrue(ok)
        changed = self.app.auth.change_password("alice@example.com", "Welcome12#_", "NewPass123!")
        self.assertTrue(changed)
        ok2 = self.app.auth.login("alice@example.com", "NewPass123!")
        self.assertTrue(ok2)


if __name__ == "__main__":
    unittest.main()
