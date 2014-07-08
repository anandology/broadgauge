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
    admin_id integer references users
);

create table trainer (
    user_id integer references users,
    city text,
    github text,
    website text,
    bio text
);
