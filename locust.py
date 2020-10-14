from locust import HttpUser, task, between


class WebsiteTestUser(HttpUser):
    wait_time = between(0.5, 1.0)

    def on_start(self):
        print("Start doing task")
        pass

    def on_stop(self):
        print("Stop doing task")
        pass

    @task
    def spin(self):
        self.client.post("http://127.0.0.1:8000/openTheBox", headers={"Content-type":"application/json"}, json={"user_id": 1}, verify=False)
