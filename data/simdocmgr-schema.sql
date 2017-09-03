-- Schema for SIMple DOCument ManaGeR
-- Copyright 2016 Joshua Kramer

create table doc_tags (
    tag_text    varchar,
    create_date varchar
);

create table doc_attributes (
    attrib_name     varchar,
    attrib_value    varchar,
    create_date     varchar
);

create table documents (
    doc_path        varchar,
    doc_filename    varchar,
    create_date     varchar,
    create_user     varchar,
    eff_date        varchar,
    doc_name        varchar
);

-- This table requires some explanation.  The autoindexer can have many rules;
-- each rule will scan the document text for a match to a particular regex,
-- and if the match is found, a tag will be added to that document in the
-- database.  This will be written in such a way that rules can be added to
-- the database at a later date and each document can be re-scanned to see if
-- the new rule matches.

create table document_log (
    doc_id          bigint,
    event_dts       varchar,
    event_subject   varchar,
    rule_name       varchar,
    event_desc      varchar
)

create table document_rules (
    rule_name       varchar,
    rule_regex      varchar,
    rule_tag        varchar
)

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

create index diad ON documents(autoindex_date);
create index dttt ON doc_tags(tag_text);
create index ndd ON n_docs_tags(doc_id);
create index ndt ON n_docs_tags(tag_id);

-- Insert some sample data:

INSERT INTO doc_tags(tag_text, create_date) VALUES ('Test-Tag-1', date('now'));
INSERT INTO doc_tags(tag_text, create_date) VALUES ('Test-Tag-2', date('now'));
INSERT INTO doc_tags(tag_text, create_date) VALUES ('Test-Tag-3', date('now'));

INSERT INTO doc_attributes(attrib_name, attrib_value, create_date) VALUES ('Test-Attrib-1', '1', date('now'));
INSERT INTO doc_attributes(attrib_name, attrib_value, create_date) VALUES ('Test-Attrib-2', 'two', date('now'));
INSERT INTO doc_attributes(attrib_name, attrib_value, create_date) VALUES ('Test-Attrib-3', 'lettuce', date('now'));

