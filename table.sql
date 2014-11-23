DROP TABLE IF EXISTS employee_info;
DROP TABLE IF EXISTS asset_info;
DROP TABLE IF EXISTS use_record;

CREATE TABLE employee_info (
	employee_id char (20) NOT NULL PRIMARY KEY,
	name char (20) NOT NULL,
	password char (20) NOT NULL,
	dept char (20) NOT NULL,
	groupname char (20),
	tel char (20),
	jabber char (20),
	email char (20) NOT NULL,
	level int NOT NULL
);

CREATE TABLE asset_info (
	asset_id char (20) NOT NULL PRIMARY KEY,
	type char (20) NOT NULL,
	state int NOT NULL,
	destination char (20),
	from_dpt char (20),
	comment varchar
);

CREATE TABLE use_record (
	id integer NOT NULL PRIMARY KEY autoincrement,
	employee_id char (20) NOT NULL REFERENCES employee_info(employee_id),
	asset_id char (20) NOT NULL REFERENCES asset_info(asset_id),
	time timestamp NOT NULL,
	comment varchar
);

