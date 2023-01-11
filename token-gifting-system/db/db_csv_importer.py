import logging
# import csv


class Import_Data:

    def __init__(self, csv_filename_and_path):
        try:
            self.source_file = open(csv_filename_and_path, 'r')
            self.table_name = ""
            self.number_of_columns = 0
            self.pk_name = ""
            self.column_names = []
            self.column_types = []
            self.number_of_records = 0
            self.table_config_data = 0
            self.table_records = 0

        except Exception as e:
            logging.error(e)
