import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest

class DashboardTests(unittest.TestCase):
    def test_team_and_filters(self):
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30).run()
        self.assertFalse(app.exception)
        app.sidebar.selectbox[0].select("Arsenal").run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, "20")
        self.assertEqual(app.metric[1].value, "60.0%")
        next(s for s in app.selectbox if s.label == "Half-time advantage").select("One goal").run()
        next(s for s in app.selectbox if s.label == "Match venue").select("Away").run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, "4")
        app.sidebar.selectbox[0].select("Liverpool").run()
        self.assertFalse(app.exception)
