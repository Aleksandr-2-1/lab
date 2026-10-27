PRAGMA foreign_keys = OFF;

DROP TABLE IF EXISTS movements;
DROP TABLE IF EXISTS equipment;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS departments;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS roles;

PRAGMA foreign_keys = ON;

CREATE TABLE roles (
    role_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role_id INTEGER NOT NULL,
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
);

CREATE TABLE departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    department_id INTEGER,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE equipment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inventory_number TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    serial_number TEXT UNIQUE,
    manufacturer TEXT,
    model TEXT,
    acquisition_date TEXT,
    cost REAL,
    status TEXT NOT NULL DEFAULT 'В наличии',
    department_id INTEGER,
    category_id INTEGER,
    employee_id INTEGER,
    FOREIGN KEY (department_id) REFERENCES departments(id),
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (employee_id) REFERENCES employees(id)
);

CREATE TABLE movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    previous_location TEXT,
    new_location TEXT,
    movement_date TEXT NOT NULL,
    return_date TEXT,
    reason TEXT,
    FOREIGN KEY (equipment_id) REFERENCES equipment(id),
    FOREIGN KEY (employee_id) REFERENCES employees(id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);