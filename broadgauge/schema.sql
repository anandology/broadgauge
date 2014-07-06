
create table organization (
    id serial primary key,
    name text,
    city text
);

create table trainer (
    id serial primary key,
    name text,
    email text unique,
    phone text,
    website text,
    city text,
    bio text
);

