-- Hats R Us: Customer Support Database Schema
-- Run this in the Supabase SQL Editor

create extension if not exists "uuid-ossp";

-- Customers
create table customers (
    id uuid primary key default uuid_generate_v4(),
    name text not null,
    email text unique not null,
    phone text,
    address text,
    membership_tier text not null default 'bronze'
        check (membership_tier in ('bronze', 'silver', 'gold')),
    created_at timestamptz not null default now()
);

-- Orders
create table orders (
    id uuid primary key default uuid_generate_v4(),
    customer_id uuid not null references customers(id),
    hat_name text not null,
    hat_style text not null
        check (hat_style in (
            'fedora', 'snapback', 'beanie', 'bucket',
            'panama', 'trucker', 'cowboy', 'beret', 'custom'
        )),
    color text not null,
    size text not null check (size in ('S', 'M', 'L', 'XL')),
    quantity int not null default 1,
    unit_price decimal(10,2) not null,
    total decimal(10,2) not null,
    status text not null default 'pending'
        check (status in ('pending', 'shipped', 'delivered', 'cancelled')),
    ordered_at timestamptz not null default now()
);

-- Support Tickets
create table support_tickets (
    id uuid primary key default uuid_generate_v4(),
    customer_id uuid not null references customers(id),
    order_id uuid references orders(id),
    subject text not null,
    description text not null,
    category text not null
        check (category in ('billing', 'order', 'product', 'return', 'other')),
    status text not null default 'open'
        check (status in ('open', 'in_progress', 'resolved', 'escalated')),
    priority text not null default 'medium'
        check (priority in ('low', 'medium', 'high')),
    created_at timestamptz not null default now()
);

-- Indexes for common query patterns
create index idx_orders_customer_id on orders(customer_id);
create index idx_orders_status on orders(status);
create index idx_support_tickets_customer_id on support_tickets(customer_id);
create index idx_support_tickets_order_id on support_tickets(order_id);
create index idx_customers_email on customers(email);
