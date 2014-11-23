drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  title text not null,
  text text not null
);

drop table if exists personnelInformation;
create table personnelInformation (
  name text primary key,
  password text not null
);

drop table if exists productInfo;
create table productInfo (
 id integer primary key autoincrement,
 productID text not null,
 productType text not null,
 username text not null,
 status text not null
);

