-- Schema for SIMple DOCument ManaGeR
-- Copyright 2016 Joshua Kramer

create table doc_tags (
        tag_text    varchar,
        last_used   varchar,
        create_date varchar
);

create table doc_attributes (
    attrib_name     varchar,
    attrib_value    varchar
)

create table documents (
    doc_path        varchar,
    doc_filename    varchar,
    create_date     varchar,
    create_user     varchar,
    doc_name        varchar
);

create table n_docs_tags (
    doc_id  bigint,
    tag_id  bigint,
    create_date varchar
);

create table n_docs_attribs (
    doc_id      bigint,
    attrib_id   bigint,
    create_date varchar
);
    

create index dttt ON doc_tags(tag_text);
create index ndd ON n_docs_tags(doc_id);
create index ndt ON n_docs_tags(tag_id);

