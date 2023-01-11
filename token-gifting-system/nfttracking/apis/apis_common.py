import logging


class api:

    def __init__(self, name):
        self.name = name
        self.rootUrl = ""
        self.parameter = ""
        self.headerOptions = None

    def set_rooturl(self, url):
        self.rootUrl = url
        logging.info(f'{self.name} url has been set to {self.rootUrl}')

    def set_parameter(self, param):
        self.parameter = param
        logging.info(f'{self.name} parameter has been set to {self.parameter}')

    def set_header(self, head):
        self.headerOptions = head
        logging.info(f'{self.name} header has been set to {self.headerOptions}')
