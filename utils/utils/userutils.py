class SerializableCommands:
    def __init__(self, user):
        self.user = user
        self._pwd = '/'
    def default(self):
        pass
    def ls(self, dirname: str='.'):
        """
        list_file
        """
        pass
    def rm(self, file_name: str):
        pass
    def cp(self, _from: str, to: str):
        pass
    def pwd(self):
        return f'f1l3://{self._pwd}'
    def exec(self, cmd, *args):
        return getattr(self, cmd, self.default)(*args)
