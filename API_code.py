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
    def export_workspace(self, workspace_json, fmu_jsons, fmu_files, connection_jsons):
        workspace_url = self.base_url + "add_full_workspace"
        workspace_get = self.base_url + "get_workspaces"

        workspace_json["fmus"] = fmu_jsons
        workspace_json["connections"] = connection_jsons

        data = {"payload" : json.dumps(workspace_json)}

        post_response = self.session.post(url = workspace_url, data = data, files = tuple(fmu_files))

        get_response = self.session.get(url=workspace_get, params={"name": workspace_json["name"]})

        return post_response.text, get_response.text
        
        
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
