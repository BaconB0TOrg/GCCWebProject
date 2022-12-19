import unittest
import mcdocker
import docker.errors as derror 

'''
- These test are not ran in order!
- all tests must begin with a test_... function delclaration
'''
class TestMCDocker(unittest.TestCase):

    # Runs before all test are complete
    @classmethod
    def setUpClass(cls):
        # Set up a minecraft server instance
        cls.mc_docker = mcdocker.make_server(threaded=False) # Set false so we can get the server generated before any of the test code runs
    
    # Checks to see if the docker was made
    def test_docker_server_made(self):
        # Test if the docker container has been make
        self.assertIsNotNone(self.mc_docker)

    # Checks to see if the docker mc server properties files can be updated correctly
    def test_docker_update_properties(self):
        default_server_properites_dict = {
            "max-players": "20",
            "motd": "test"
        }
        self.assertTrue(mcdocker.update_server_properties(container_id=self.mc_docker, updated_properties=default_server_properites_dict))
        self.assertFalse(mcdocker.update_server_properties(container_id=None))
        self.assertFalse(mcdocker.update_server_properties(container_id=self.mc_docker, updated_properties={"dafdsa": "231"}))

    # Checks to see if docker containers are still controllable
    def test_docker_controll(self):
        self.assertTrue(mcdocker.stop_docker(self.mc_docker))
        self.assertTrue(mcdocker.start_docker(self.mc_docker))
        self.assertFalse(mcdocker.stop_docker(None))
        self.assertFalse(mcdocker.start_docker(None))

    # Runs after all test have been concluded
    @classmethod
    def tearDownClass(cls):
        # Removes the docker container
        mcdocker.remove_docker(cls.mc_docker)

    


if __name__ == "__main__":
    # Allows it to be ran with python test_mcdocker.py instead of python -m unittest test_mcdocker.py
    unittest.main()
