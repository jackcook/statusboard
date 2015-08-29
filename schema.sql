create table if not exists checks (
  id integer primary key autoincrement,
  type text not null,
  payload text not null
)
