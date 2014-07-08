create table users (
    id serial primary key,
    name text,
    email text unique,
    phone text
);

create table organization (
    id serial primary key,
    name text,
    city text,
    admin_id integer references users,
    admin_role text
);

create table trainer (
    user_id integer references users unique,
    city text,
    github text,
    website text,
    bio text
);