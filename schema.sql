create table if not exists data (
  id integer primary key autoincrement,
  timestamp text not null,
  time text not null
);

create table if not exists ping (
  id integer primary key autoincrement,
  timestamp text not null,
  time text not null
);
