from sese_cli import SeseCli
from sese_qt import SeseQt
class SeseFactory:
    def create_cli(self):
        raise NotImplementedError("This method should be overridden.")

    def create_Qt(self):
        raise NotImplementedError("This method should be overridden.")

class ConcreteSeseFactory(SeseFactory):
    
    def __init__(self, config) -> None:
        self.config=config
        
    def create_cli(self):
        return SeseCli(self.config)

    def create_Qt(self):
        return SeseQt()