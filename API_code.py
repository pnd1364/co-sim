import json
import requests

class APISession():

    base_url = "http://127.0.0.1:8000/co-simAPI/"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.get(self.base_url + "docs")
        self.update_header()
        self.logged_in = False


    def update_header(self):
        # update headers
        headers = {"X-CSRFToken": self.session.cookies.get("csrftoken"), "Referer": self.base_url}
        self.session.headers.update(headers)


    # TODO: implement import_workspace into API first
    def import_workspace(session, workspace_name):
        return 0


    # TODO: figure out if one part fails, what do we do? like break and delete everything?
    def export_workspace(self, workspace_json, fmu_jsons, fmu_paths, connection_jsons):
        workspace_url = self.base_url + "add_workspace"
        fmu_url = self.base_url + "add_fmu"
        connection_url = self.base_url + "add_connection"

        response = self.session.post(url = workspace_url, data = json.dumps(workspace_json))

        total_response_text = response.text

        if response.status_code == 200:
            for fmu_json, fmu_path in zip(fmu_jsons, fmu_paths):
                # data does NOT have json.dumps because content type is not application/json, instead it is multipart so with Form style
                fmu_response = self.session.post(url = fmu_url, data = fmu_json, files = {'file': (fmu_json["fmu_name"], open(fmu_path, 'rb'))})
                total_response_text = total_response_text + fmu_response.text

            for connection_json in connection_jsons:
                connection_response = self.session.post(url = connection_url, data = json.dumps(connection_json))
                total_response_text = total_response_text + connection_response.text

        return total_response_text
        
        
    def login(self, username, password):
        """
        Logs in to the API with the given username and password.
        Returns success message and updates header with csrftoken if logged in.
        """
        url = self.base_url + "login"
        data = {'username': username, 'password': password}
        
        response = self.session.post(url, data=json.dumps(data))

        if response.status_code == 200:
            # update headers
            self.update_header()
            self.logged_in = True

            return response.status_code, response.text
        else:
            return response.status_code, response.text
        
    def register(self, username, password):
        """
        Registers a new user with the given username and password.
        Returns a success message and updates header with csrftoken if successful.
        """
        url = self.base_url + "register"
        
        data = {'username': username, 'password': password}

        # post data to session
        response = self.session.post(url, data = json.dumps(data))
        
        if response.status_code == 201:
            # update headers
            self.update_header()

            # return output to be print in run.py
            return response.status_code, response.text
        else:
            return response.status_code, response.text
