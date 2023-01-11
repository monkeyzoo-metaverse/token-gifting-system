# db.

## Overview

This is for handling everything to do with the database 

## Modules list and classes

+ `` db_config. ``

    + `` class DB_status_record: ``
    + `` class DB_Config: ``
    
+ `` yms_db_test. ``
    + `` class DB_initalsation: ``
    + `` class DB_tools:``
    
## db_config.DB_status_record:

### Class Constants

The below constants enumerate the current database status    
    
+ ``DB_NOT_PRESENT = 0`` No valid database file is present

+ ``DB_STATUS_EMPTY = 1``Database id present but only contains status table

+ ``DB_STATUS_READY = 2``Database is ready to be used

+ ``DB_STATUS_UNKNOWN = 3``Database has unknown error


### Initalisation 
``.DB_status_record(status, timestamp=None, status_record_id=None)``

+ ``status`` Takes a class constant of the bases current state
+ ``timestamp`` Takes float of the current timestamp (default: ``None``)
+ ``status_record_id`` Takes the Primary key of the status record (default: ``None``)

#### Example

``DB_status_record(status=DB_Config.DB_STATUS_EMPTY, timestamp=time.time(), status_record_id=1)``

### Methods

``set_status_record_id(status_record_id)``

``get_status_record_id()``

``get_status(self)``

    

## yms_db_test.DB_initalsation:

### Methods 

``.connect(file_path=None)``

``.create_new_db(file_path=None)``

``.create_db_table( table_name, pri_key_name, pri_key_type, column_names=None, column_types=None)``

``.read_all_db_status_records_from_database()``

``.read_latest_db_status_record_from_database()``

returns [.DB_status_record]
    


