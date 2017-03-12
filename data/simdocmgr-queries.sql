-- Queries used to find documents per tag

select
    d.doc_path,
    d.doc_filename,
    d.create_date,
    d.create_user,
    d.eff_date,
    dt.tag_text,
    ndt.create_date
from
    doc_tags dt
inner join n_docs_tags ndt on ndt.tag_id = dt.rowid
inner join documents d on d.rowid = ndt.doc_id
where
    dt.tag_text like '734%';

