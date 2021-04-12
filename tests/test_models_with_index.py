def test_model_with_one_index():
    ddl = """
    
    CREATE table schema_name.task_requests (
        runid                decimal(21) not null
    ,job_id               decimal(21) not null
    ,object_id            varchar(100) not null default 'none'
    ,pipeline_id          varchar(100) not null default 'none'
    ,sequence             smallint not null
    ,processor_id         varchar(100) not null
    ,source_file          varchar(1000) not null default 'none'
    ,job_args             varchar array null
    ,request_time         timestamp not null default now()
    ,status               varchar(25) not null
    ,status_update_time   timestamp null default now()
    ) ;
    create unique index task_requests_pk on schema_name.task_requests (runid) ;
    
    """
    pass
