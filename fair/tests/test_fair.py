import unittest
import os
from fair import app
from projects.models import Project


class FairTestCase(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["DEBUG"] = True
        folders = {}
        folders["DATA_FOLDER"] = app.config["DATA_FOLDER"] = os.path.join(
            os.getcwd(), "tests/data"
        )

        folders["UPLOAD_FOLDER"] = app.config["UPLOAD_FOLDER"] = os.path.join(
            os.getcwd(), "tests/images"
        )
        app.config["WTF_CSRF_ENABLED"] = True
        # Create required folders for the application if they don't exist
        for _, folder in folders.items():
            try:
                os.makedirs(folder)
                print("Created: " + folder)
            except FileExistsError:
                pass

        app.config["WTF_CSRF_ENABLED"] = False
        # Override default DB setting
        # -> use a testing db instead of the default
        app.config["DB"] = os.path.join(app.config["DATA_FOLDER"], "dataset_test")
        self.app = app.test_client()

    def tearDown(self):
        # Clean up
        Project.clear()
        self.assertTrue(len(Project.get_all()) == 0)

    def test_dummy(self):
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
