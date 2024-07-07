import json
import unittest

from module.structures import SubmissionData, UserData
from module.submission import fetch_submissions, get_first_ac
from module.utils import *
from module.config import Config

config = Config("../config.json")
oj_url = config.get_config("url")


class TestUtil(unittest.TestCase):
    def test_qq(self):
        number = config.get_config("test")['qq']['number']
        name = config.get_config("test")['qq']['name']
        self.assertEqual(get_qq_name(number), name)

    def test_reload_rp(self):
        req_type = "rp"
        self.assertTrue(reload_stats(config, oj_url, req_type))

    def test_reload_problemStat(self):
        req_type = "problemStat"
        self.assertTrue(reload_stats(config, oj_url, req_type))


class TestFetch(unittest.TestCase):
    def test_fetch_submissions_yesterday(self):
        result = fetch_submissions(config, True)
        with open("submission_result_yesterday.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(result, default=lambda o: o.__dict__, ensure_ascii=False, indent=4))
            f.close()
        self.assertTrue(len(result) > 0)

    def test_fetch_submissions_today(self):
        result = fetch_submissions(config, False)
        with open("submission_result_today.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(result, default=lambda o: o.__dict__, ensure_ascii=False, indent=4))
            f.close()
        self.assertTrue(len(result) > 0)

    def test_get_first_ac(self):
        yesterday_submissions = json.load(open("submission_result_yesterday.json", "r", encoding="utf-8"))
        today_submissions = json.load(open("submission_result_today.json", "r", encoding="utf-8"))
        submissions = []
        for submission in yesterday_submissions:
            submissions.append(SubmissionData(UserData(submission['user']['name'], submission['user']['uid']),
                                              submission['score'], submission['verdict'], submission['problem_name'],
                                              submission['at']))
        yesterday_submissions = submissions
        submissions = []
        for submission in today_submissions:
            submissions.append(SubmissionData(UserData(submission['user']['name'], submission['user']['uid']),
                                              submission['score'], submission['verdict'], submission['problem_name'],
                                              submission['at']))
        today_submissions = submissions
        result = {"yesterday": get_first_ac(yesterday_submissions), "today": get_first_ac(today_submissions)}
        with open("first_ac.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(result, default=lambda o: o.__dict__, ensure_ascii=False, indent=4))
            f.close()
        self.assertTrue(len(result) > 0)


if __name__ == '__main__':
    unittest.main()
