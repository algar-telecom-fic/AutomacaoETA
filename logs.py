class logs:
    def __init__(self):
        self.obj = {
            "userRequest": "",
            "flag": "",
            "weekday": "",
            "date": "",
            "time": "",
            "command": "",
            "hostname": "",
            "userRemote": "",
            "host": "",
            "port": "",
            "success": "",
            "error": ""
            }

    def printResult(self):
        values = self.obj
        return values["userRequest"] + str(values["flag"]) + values["weekday"] + values["date"] + values["time"] + values["command"] + values["hostname"] + values["userRemote"] + values["host"] + values["port"] + str(values["success"])