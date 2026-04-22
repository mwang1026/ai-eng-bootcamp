-- Hats R Us: Seed Data
-- Run this in the Supabase SQL Editor after 01_create_tables.sql
-- Uses hardcoded UUIDs for test fixture rows (first few of each table)

-- ============================================================
-- CUSTOMERS (20 total: 12 bronze, 5 silver, 3 gold)
-- ============================================================
insert into customers (id, name, email, phone, address, membership_tier, created_at) values
-- Gold members (3)
('a0000000-0000-0000-0000-000000000001', 'Alice Chen', 'alice.chen@email.com', '555-0101', '123 Main St, Portland, OR 97201', 'gold', now() - interval '2 years'),
('a0000000-0000-0000-0000-000000000002', 'Bob Martinez', 'bob.martinez@email.com', '555-0102', '456 Oak Ave, Austin, TX 78701', 'gold', now() - interval '18 months'),
('a0000000-0000-0000-0000-000000000003', 'Carol Johnson', 'carol.johnson@email.com', '555-0103', '789 Pine Rd, Denver, CO 80201', 'gold', now() - interval '1 year'),
-- Silver members (5)
('a0000000-0000-0000-0000-000000000004', 'David Kim', 'david.kim@email.com', '555-0104', '321 Elm St, Seattle, WA 98101', 'silver', now() - interval '10 months'),
('a0000000-0000-0000-0000-000000000005', 'Eva Rodriguez', 'eva.rodriguez@email.com', '555-0105', '654 Maple Dr, Miami, FL 33101', 'silver', now() - interval '9 months'),
('a0000000-0000-0000-0000-000000000006', 'Frank O''Brien', 'frank.obrien@email.com', '555-0106', '987 Cedar Ln, Chicago, IL 60601', 'silver', now() - interval '8 months'),
('a0000000-0000-0000-0000-000000000007', 'Grace Lee', 'grace.lee@email.com', '555-0107', '147 Birch Ct, San Francisco, CA 94101', 'silver', now() - interval '7 months'),
('a0000000-0000-0000-0000-000000000008', 'Henry Patel', 'henry.patel@email.com', '555-0108', '258 Walnut Way, Boston, MA 02101', 'silver', now() - interval '6 months'),
-- Bronze members (12)
('a0000000-0000-0000-0000-000000000009', 'Iris Thompson', 'iris.thompson@email.com', '555-0109', '369 Ash Blvd, Nashville, TN 37201', 'bronze', now() - interval '5 months'),
('a0000000-0000-0000-0000-000000000010', 'Jack Wilson', 'jack.wilson@email.com', '555-0110', '480 Spruce St, Minneapolis, MN 55401', 'bronze', now() - interval '4 months'),
('a0000000-0000-0000-0000-000000000011', 'Karen Davis', 'karen.davis@email.com', '555-0111', '591 Cypress Ave, Phoenix, AZ 85001', 'bronze', now() - interval '4 months'),
('a0000000-0000-0000-0000-000000000012', 'Leo Nguyen', 'leo.nguyen@email.com', '555-0112', '702 Poplar Rd, Atlanta, GA 30301', 'bronze', now() - interval '3 months'),
('a0000000-0000-0000-0000-000000000013', 'Mia Garcia', 'mia.garcia@email.com', '555-0113', '813 Willow St, San Diego, CA 92101', 'bronze', now() - interval '3 months'),
('a0000000-0000-0000-0000-000000000014', 'Noah Brown', 'noah.brown@email.com', '555-0114', '924 Juniper Dr, Raleigh, NC 27601', 'bronze', now() - interval '2 months'),
('a0000000-0000-0000-0000-000000000015', 'Olivia Taylor', 'olivia.taylor@email.com', '555-0115', '135 Magnolia Ln, Portland, ME 04101', 'bronze', now() - interval '2 months'),
('a0000000-0000-0000-0000-000000000016', 'Peter Singh', 'peter.singh@email.com', '555-0116', '246 Redwood Ct, Sacramento, CA 95801', 'bronze', now() - interval '1 month'),
('a0000000-0000-0000-0000-000000000017', 'Quinn Adams', 'quinn.adams@email.com', '555-0117', '357 Sequoia Way, Salt Lake City, UT 84101', 'bronze', now() - interval '1 month'),
('a0000000-0000-0000-0000-000000000018', 'Rachel Moore', 'rachel.moore@email.com', '555-0118', '468 Dogwood Blvd, Charlotte, NC 28201', 'bronze', now() - interval '3 weeks'),
('a0000000-0000-0000-0000-000000000019', 'Sam Cooper', 'sam.cooper@email.com', '555-0119', '579 Hemlock St, Columbus, OH 43201', 'bronze', now() - interval '2 weeks'),
('a0000000-0000-0000-0000-000000000020', 'Tina Wright', 'tina.wright@email.com', '555-0120', '680 Sycamore Ave, Indianapolis, IN 46201', 'bronze', now() - interval '1 week');

-- ============================================================
-- ORDERS (100 total)
-- Spread across statuses, dates, and hat styles
-- Key test fixtures:
--   b...001: Alice (gold), delivered 10 days ago — eligible for return
--   b...002: Alice (gold), delivered 45 days ago — eligible (gold gets 60 days)
--   b...003: Bob (gold), delivered 70 days ago — NOT eligible (past 60 days)
--   b...004: David (silver), delivered 15 days ago — eligible for return
--   b...005: David (silver), delivered 40 days ago — NOT eligible (silver gets 30 days)
--   b...006: Iris (bronze), custom hat, delivered 5 days ago — NOT eligible (custom)
--   b...007: Iris (bronze), delivered 20 days ago — eligible for return
-- ============================================================
insert into orders (id, customer_id, hat_name, hat_style, color, size, quantity, unit_price, total, status, ordered_at) values
-- Test fixture orders (hardcoded UUIDs for test references)
('b0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001', 'Classic Wool Fedora', 'fedora', 'charcoal', 'M', 1, 89.99, 89.99, 'delivered', now() - interval '10 days'),
('b0000000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-000000000001', 'Summer Straw Panama', 'panama', 'natural', 'L', 1, 75.00, 75.00, 'delivered', now() - interval '45 days'),
('b0000000-0000-0000-0000-000000000003', 'a0000000-0000-0000-0000-000000000002', 'Vintage Leather Cowboy', 'cowboy', 'brown', 'XL', 1, 129.99, 129.99, 'delivered', now() - interval '70 days'),
('b0000000-0000-0000-0000-000000000004', 'a0000000-0000-0000-0000-000000000004', 'Urban Snapback Cap', 'snapback', 'black', 'M', 2, 34.99, 69.98, 'delivered', now() - interval '15 days'),
('b0000000-0000-0000-0000-000000000005', 'a0000000-0000-0000-0000-000000000004', 'Cozy Winter Beanie', 'beanie', 'navy', 'S', 1, 29.99, 29.99, 'delivered', now() - interval '40 days'),
('b0000000-0000-0000-0000-000000000006', 'a0000000-0000-0000-0000-000000000009', 'Custom Embroidered Logo Cap', 'custom', 'red', 'L', 3, 45.00, 135.00, 'delivered', now() - interval '5 days'),
('b0000000-0000-0000-0000-000000000007', 'a0000000-0000-0000-0000-000000000009', 'Outdoor Bucket Hat', 'bucket', 'olive', 'M', 1, 39.99, 39.99, 'delivered', now() - interval '20 days'),

-- Alice Chen (gold) — additional orders
('b0000000-0000-0000-0000-000000000008', 'a0000000-0000-0000-0000-000000000001', 'Elegant French Beret', 'beret', 'burgundy', 'S', 1, 55.00, 55.00, 'shipped', now() - interval '3 days'),
('b0000000-0000-0000-0000-000000000009', 'a0000000-0000-0000-0000-000000000001', 'Trail Trucker Cap', 'trucker', 'forest green', 'L', 1, 28.99, 28.99, 'delivered', now() - interval '90 days'),
('b0000000-0000-0000-0000-000000000010', 'a0000000-0000-0000-0000-000000000001', 'Premium Wool Fedora', 'fedora', 'black', 'M', 1, 110.00, 110.00, 'pending', now() - interval '1 day'),

-- Bob Martinez (gold) — additional orders
('b0000000-0000-0000-0000-000000000011', 'a0000000-0000-0000-0000-000000000002', 'Beach Bucket Hat', 'bucket', 'sky blue', 'L', 2, 35.00, 70.00, 'delivered', now() - interval '25 days'),
('b0000000-0000-0000-0000-000000000012', 'a0000000-0000-0000-0000-000000000002', 'Classic Snapback', 'snapback', 'white', 'M', 1, 32.99, 32.99, 'shipped', now() - interval '5 days'),
('b0000000-0000-0000-0000-000000000013', 'a0000000-0000-0000-0000-000000000002', 'Winter Knit Beanie', 'beanie', 'gray', 'M', 3, 24.99, 74.97, 'delivered', now() - interval '120 days'),

-- Carol Johnson (gold) — orders
('b0000000-0000-0000-0000-000000000014', 'a0000000-0000-0000-0000-000000000003', 'Designer Panama Hat', 'panama', 'cream', 'M', 1, 95.00, 95.00, 'delivered', now() - interval '12 days'),
('b0000000-0000-0000-0000-000000000015', 'a0000000-0000-0000-0000-000000000003', 'Rancher Cowboy Hat', 'cowboy', 'tan', 'L', 1, 145.00, 145.00, 'delivered', now() - interval '50 days'),
('b0000000-0000-0000-0000-000000000016', 'a0000000-0000-0000-0000-000000000003', 'Custom Name Trucker', 'custom', 'navy', 'M', 1, 55.00, 55.00, 'delivered', now() - interval '8 days'),
('b0000000-0000-0000-0000-000000000017', 'a0000000-0000-0000-0000-000000000003', 'Artisan Beret', 'beret', 'olive', 'S', 1, 62.00, 62.00, 'cancelled', now() - interval '30 days'),

-- David Kim (silver) — additional orders
('b0000000-0000-0000-0000-000000000018', 'a0000000-0000-0000-0000-000000000004', 'City Fedora', 'fedora', 'navy', 'L', 1, 79.99, 79.99, 'delivered', now() - interval '60 days'),
('b0000000-0000-0000-0000-000000000019', 'a0000000-0000-0000-0000-000000000004', 'Sport Trucker Cap', 'trucker', 'red', 'M', 1, 26.99, 26.99, 'pending', now() - interval '2 days'),

-- Eva Rodriguez (silver) — orders
('b0000000-0000-0000-0000-000000000020', 'a0000000-0000-0000-0000-000000000005', 'Tropical Bucket Hat', 'bucket', 'coral', 'S', 1, 42.00, 42.00, 'delivered', now() - interval '18 days'),
('b0000000-0000-0000-0000-000000000021', 'a0000000-0000-0000-0000-000000000005', 'Boho Beret', 'beret', 'rust', 'M', 1, 48.00, 48.00, 'delivered', now() - interval '35 days'),
('b0000000-0000-0000-0000-000000000022', 'a0000000-0000-0000-0000-000000000005', 'Festival Snapback', 'snapback', 'tie-dye', 'L', 2, 38.00, 76.00, 'shipped', now() - interval '4 days'),

-- Frank O'Brien (silver) — orders
('b0000000-0000-0000-0000-000000000023', 'a0000000-0000-0000-0000-000000000006', 'Irish Tweed Flat Cap', 'fedora', 'tweed', 'L', 1, 85.00, 85.00, 'delivered', now() - interval '22 days'),
('b0000000-0000-0000-0000-000000000024', 'a0000000-0000-0000-0000-000000000006', 'Chunky Knit Beanie', 'beanie', 'cream', 'M', 2, 32.00, 64.00, 'delivered', now() - interval '55 days'),
('b0000000-0000-0000-0000-000000000025', 'a0000000-0000-0000-0000-000000000006', 'Western Cowboy Hat', 'cowboy', 'black', 'XL', 1, 135.00, 135.00, 'pending', now() - interval '1 day'),

-- Grace Lee (silver) — orders
('b0000000-0000-0000-0000-000000000026', 'a0000000-0000-0000-0000-000000000007', 'Minimalist Bucket', 'bucket', 'beige', 'S', 1, 38.00, 38.00, 'delivered', now() - interval '14 days'),
('b0000000-0000-0000-0000-000000000027', 'a0000000-0000-0000-0000-000000000007', 'Cashmere Beret', 'beret', 'charcoal', 'M', 1, 78.00, 78.00, 'delivered', now() - interval '28 days'),
('b0000000-0000-0000-0000-000000000028', 'a0000000-0000-0000-0000-000000000007', 'Tech Trucker Cap', 'trucker', 'black', 'M', 1, 30.00, 30.00, 'shipped', now() - interval '6 days'),

-- Henry Patel (silver) — orders
('b0000000-0000-0000-0000-000000000029', 'a0000000-0000-0000-0000-000000000008', 'Gentleman''s Fedora', 'fedora', 'slate', 'L', 1, 99.00, 99.00, 'delivered', now() - interval '32 days'),
('b0000000-0000-0000-0000-000000000030', 'a0000000-0000-0000-0000-000000000008', 'Custom Monogram Panama', 'custom', 'white', 'M', 1, 120.00, 120.00, 'delivered', now() - interval '16 days'),

-- Iris Thompson (bronze) — additional orders
('b0000000-0000-0000-0000-000000000031', 'a0000000-0000-0000-0000-000000000009', 'Retro Snapback', 'snapback', 'vintage blue', 'M', 1, 36.00, 36.00, 'delivered', now() - interval '45 days'),
('b0000000-0000-0000-0000-000000000032', 'a0000000-0000-0000-0000-000000000009', 'Sherpa-Lined Beanie', 'beanie', 'charcoal', 'L', 1, 34.99, 34.99, 'cancelled', now() - interval '10 days'),

-- Jack Wilson (bronze) — orders
('b0000000-0000-0000-0000-000000000033', 'a0000000-0000-0000-0000-000000000010', 'Explorer Bucket Hat', 'bucket', 'khaki', 'L', 1, 44.00, 44.00, 'delivered', now() - interval '8 days'),
('b0000000-0000-0000-0000-000000000034', 'a0000000-0000-0000-0000-000000000010', 'Rodeo Cowboy Hat', 'cowboy', 'brown', 'XL', 1, 125.00, 125.00, 'delivered', now() - interval '65 days'),
('b0000000-0000-0000-0000-000000000035', 'a0000000-0000-0000-0000-000000000010', 'Fleece Beanie', 'beanie', 'black', 'M', 2, 22.99, 45.98, 'shipped', now() - interval '3 days'),
('b0000000-0000-0000-0000-000000000036', 'a0000000-0000-0000-0000-000000000010', 'Classic Panama', 'panama', 'straw', 'L', 1, 68.00, 68.00, 'delivered', now() - interval '25 days'),

-- Karen Davis (bronze) — orders
('b0000000-0000-0000-0000-000000000037', 'a0000000-0000-0000-0000-000000000011', 'Wide Brim Sun Hat', 'bucket', 'white', 'M', 1, 48.00, 48.00, 'delivered', now() - interval '11 days'),
('b0000000-0000-0000-0000-000000000038', 'a0000000-0000-0000-0000-000000000011', 'Vintage Fedora', 'fedora', 'olive', 'S', 1, 92.00, 92.00, 'delivered', now() - interval '42 days'),
('b0000000-0000-0000-0000-000000000039', 'a0000000-0000-0000-0000-000000000011', 'Pom-Pom Beanie', 'beanie', 'pink', 'S', 3, 19.99, 59.97, 'delivered', now() - interval '7 days'),

-- Leo Nguyen (bronze) — orders
('b0000000-0000-0000-0000-000000000040', 'a0000000-0000-0000-0000-000000000012', 'Street Snapback', 'snapback', 'black', 'M', 1, 31.00, 31.00, 'delivered', now() - interval '19 days'),
('b0000000-0000-0000-0000-000000000041', 'a0000000-0000-0000-0000-000000000012', 'Denim Trucker Cap', 'trucker', 'indigo', 'L', 1, 33.00, 33.00, 'delivered', now() - interval '48 days'),
('b0000000-0000-0000-0000-000000000042', 'a0000000-0000-0000-0000-000000000012', 'Faux Fur Trapper', 'beanie', 'brown', 'XL', 1, 56.00, 56.00, 'shipped', now() - interval '2 days'),

-- Mia Garcia (bronze) — orders
('b0000000-0000-0000-0000-000000000043', 'a0000000-0000-0000-0000-000000000013', 'Raffia Sun Hat', 'panama', 'natural', 'M', 1, 72.00, 72.00, 'delivered', now() - interval '13 days'),
('b0000000-0000-0000-0000-000000000044', 'a0000000-0000-0000-0000-000000000013', 'Floral Bucket Hat', 'bucket', 'floral print', 'S', 1, 41.00, 41.00, 'delivered', now() - interval '33 days'),
('b0000000-0000-0000-0000-000000000045', 'a0000000-0000-0000-0000-000000000013', 'Leather Beret', 'beret', 'black', 'M', 1, 65.00, 65.00, 'cancelled', now() - interval '20 days'),

-- Noah Brown (bronze) — orders
('b0000000-0000-0000-0000-000000000046', 'a0000000-0000-0000-0000-000000000014', 'Mesh Trucker Cap', 'trucker', 'white/blue', 'L', 2, 25.99, 51.98, 'delivered', now() - interval '9 days'),
('b0000000-0000-0000-0000-000000000047', 'a0000000-0000-0000-0000-000000000014', 'Heritage Cowboy Hat', 'cowboy', 'camel', 'L', 1, 140.00, 140.00, 'delivered', now() - interval '75 days'),
('b0000000-0000-0000-0000-000000000048', 'a0000000-0000-0000-0000-000000000014', 'Ribbed Beanie', 'beanie', 'maroon', 'M', 1, 27.00, 27.00, 'pending', now() - interval '1 day'),

-- Olivia Taylor (bronze) — orders
('b0000000-0000-0000-0000-000000000049', 'a0000000-0000-0000-0000-000000000015', 'Garden Party Hat', 'panama', 'lavender', 'S', 1, 82.00, 82.00, 'delivered', now() - interval '16 days'),
('b0000000-0000-0000-0000-000000000050', 'a0000000-0000-0000-0000-000000000015', 'Wool Cloche', 'beret', 'plum', 'S', 1, 58.00, 58.00, 'delivered', now() - interval '38 days'),
('b0000000-0000-0000-0000-000000000051', 'a0000000-0000-0000-0000-000000000015', 'Custom Wedding Fascinator', 'custom', 'ivory', 'M', 1, 150.00, 150.00, 'delivered', now() - interval '6 days'),

-- Peter Singh (bronze) — orders
('b0000000-0000-0000-0000-000000000052', 'a0000000-0000-0000-0000-000000000016', 'Turban-Style Wrap', 'beanie', 'saffron', 'L', 1, 45.00, 45.00, 'delivered', now() - interval '21 days'),
('b0000000-0000-0000-0000-000000000053', 'a0000000-0000-0000-0000-000000000016', 'Fitted Snapback', 'snapback', 'gray', 'M', 1, 36.00, 36.00, 'shipped', now() - interval '4 days'),
('b0000000-0000-0000-0000-000000000054', 'a0000000-0000-0000-0000-000000000016', 'Safari Bucket Hat', 'bucket', 'tan', 'L', 1, 46.00, 46.00, 'delivered', now() - interval '55 days'),

-- Quinn Adams (bronze) — orders
('b0000000-0000-0000-0000-000000000055', 'a0000000-0000-0000-0000-000000000017', 'Mountaineer Fedora', 'fedora', 'forest green', 'L', 1, 105.00, 105.00, 'delivered', now() - interval '17 days'),
('b0000000-0000-0000-0000-000000000056', 'a0000000-0000-0000-0000-000000000017', 'Camo Trucker Cap', 'trucker', 'camo', 'XL', 1, 28.00, 28.00, 'delivered', now() - interval '44 days'),
('b0000000-0000-0000-0000-000000000057', 'a0000000-0000-0000-0000-000000000017', 'Angora Beret', 'beret', 'peach', 'S', 1, 70.00, 70.00, 'delivered', now() - interval '10 days'),

-- Rachel Moore (bronze) — orders
('b0000000-0000-0000-0000-000000000058', 'a0000000-0000-0000-0000-000000000018', 'Cotton Bucket Hat', 'bucket', 'light blue', 'M', 1, 35.00, 35.00, 'delivered', now() - interval '14 days'),
('b0000000-0000-0000-0000-000000000059', 'a0000000-0000-0000-0000-000000000018', 'Cable Knit Beanie', 'beanie', 'cream', 'S', 2, 28.00, 56.00, 'delivered', now() - interval '5 days'),
('b0000000-0000-0000-0000-000000000060', 'a0000000-0000-0000-0000-000000000018', 'Straw Cowboy Hat', 'cowboy', 'natural', 'M', 1, 88.00, 88.00, 'pending', now() - interval '1 day'),

-- Sam Cooper (bronze) — orders
('b0000000-0000-0000-0000-000000000061', 'a0000000-0000-0000-0000-000000000019', 'Dad Cap', 'snapback', 'washed blue', 'M', 1, 24.99, 24.99, 'delivered', now() - interval '11 days'),
('b0000000-0000-0000-0000-000000000062', 'a0000000-0000-0000-0000-000000000019', 'Corduroy Bucket Hat', 'bucket', 'mustard', 'L', 1, 40.00, 40.00, 'shipped', now() - interval '3 days'),
('b0000000-0000-0000-0000-000000000063', 'a0000000-0000-0000-0000-000000000019', 'Merino Wool Beanie', 'beanie', 'heather gray', 'M', 1, 38.00, 38.00, 'delivered', now() - interval '28 days'),

-- Tina Wright (bronze) — orders
('b0000000-0000-0000-0000-000000000064', 'a0000000-0000-0000-0000-000000000020', 'Embroidered Snapback', 'snapback', 'burgundy', 'S', 1, 34.00, 34.00, 'delivered', now() - interval '7 days'),
('b0000000-0000-0000-0000-000000000065', 'a0000000-0000-0000-0000-000000000020', 'Floppy Sun Hat', 'panama', 'blush', 'M', 1, 62.00, 62.00, 'delivered', now() - interval '22 days'),
('b0000000-0000-0000-0000-000000000066', 'a0000000-0000-0000-0000-000000000020', 'Thermal Beanie', 'beanie', 'dark green', 'L', 1, 26.00, 26.00, 'delivered', now() - interval '50 days'),

-- Additional orders to reach 100 (spread across customers)
-- Alice Chen
('b0000000-0000-0000-0000-000000000067', 'a0000000-0000-0000-0000-000000000001', 'Bucket Rain Hat', 'bucket', 'yellow', 'M', 1, 42.00, 42.00, 'delivered', now() - interval '130 days'),
('b0000000-0000-0000-0000-000000000068', 'a0000000-0000-0000-0000-000000000001', 'Snapback Collection', 'snapback', 'assorted', 'M', 4, 30.00, 120.00, 'delivered', now() - interval '100 days'),
-- Bob Martinez
('b0000000-0000-0000-0000-000000000069', 'a0000000-0000-0000-0000-000000000002', 'Trucker Mesh Cap', 'trucker', 'orange', 'L', 1, 27.00, 27.00, 'delivered', now() - interval '80 days'),
('b0000000-0000-0000-0000-000000000070', 'a0000000-0000-0000-0000-000000000002', 'Panama Day Hat', 'panama', 'sand', 'M', 1, 70.00, 70.00, 'cancelled', now() - interval '40 days'),
-- Carol Johnson
('b0000000-0000-0000-0000-000000000071', 'a0000000-0000-0000-0000-000000000003', 'Sequin Party Hat', 'beret', 'gold', 'S', 1, 55.00, 55.00, 'delivered', now() - interval '95 days'),
('b0000000-0000-0000-0000-000000000072', 'a0000000-0000-0000-0000-000000000003', 'Slouchy Beanie', 'beanie', 'purple', 'M', 2, 25.00, 50.00, 'delivered', now() - interval '3 days'),
-- David Kim
('b0000000-0000-0000-0000-000000000073', 'a0000000-0000-0000-0000-000000000004', 'Plaid Trucker', 'trucker', 'plaid', 'L', 1, 32.00, 32.00, 'delivered', now() - interval '85 days'),
('b0000000-0000-0000-0000-000000000074', 'a0000000-0000-0000-0000-000000000004', 'Cowboy Dress Hat', 'cowboy', 'silver', 'L', 1, 155.00, 155.00, 'delivered', now() - interval '7 days'),
-- Eva Rodriguez
('b0000000-0000-0000-0000-000000000075', 'a0000000-0000-0000-0000-000000000005', 'Neon Snapback', 'snapback', 'neon pink', 'M', 1, 29.99, 29.99, 'delivered', now() - interval '72 days'),
('b0000000-0000-0000-0000-000000000076', 'a0000000-0000-0000-0000-000000000005', 'Straw Beach Hat', 'panama', 'straw', 'S', 1, 58.00, 58.00, 'delivered', now() - interval '6 days'),
-- Frank O'Brien
('b0000000-0000-0000-0000-000000000077', 'a0000000-0000-0000-0000-000000000006', 'Paperboy Cap', 'fedora', 'herringbone', 'M', 1, 78.00, 78.00, 'delivered', now() - interval '88 days'),
('b0000000-0000-0000-0000-000000000078', 'a0000000-0000-0000-0000-000000000006', 'Rain Bucket Hat', 'bucket', 'navy', 'L', 1, 44.00, 44.00, 'delivered', now() - interval '4 days'),
-- Grace Lee
('b0000000-0000-0000-0000-000000000079', 'a0000000-0000-0000-0000-000000000007', 'Silk Headwrap', 'beret', 'teal', 'M', 1, 52.00, 52.00, 'delivered', now() - interval '62 days'),
('b0000000-0000-0000-0000-000000000080', 'a0000000-0000-0000-0000-000000000007', 'Wool Fedora Deluxe', 'fedora', 'camel', 'S', 1, 115.00, 115.00, 'delivered', now() - interval '9 days'),
-- Henry Patel
('b0000000-0000-0000-0000-000000000081', 'a0000000-0000-0000-0000-000000000008', 'Cricket Cap', 'snapback', 'white', 'L', 1, 30.00, 30.00, 'delivered', now() - interval '77 days'),
('b0000000-0000-0000-0000-000000000082', 'a0000000-0000-0000-0000-000000000008', 'Velvet Beret', 'beret', 'midnight blue', 'M', 1, 68.00, 68.00, 'delivered', now() - interval '2 days'),
-- Jack Wilson
('b0000000-0000-0000-0000-000000000083', 'a0000000-0000-0000-0000-000000000010', 'Hunting Cap', 'trucker', 'camo green', 'XL', 1, 29.00, 29.00, 'delivered', now() - interval '58 days'),
('b0000000-0000-0000-0000-000000000084', 'a0000000-0000-0000-0000-000000000010', 'Canvas Bucket Hat', 'bucket', 'army green', 'L', 1, 37.00, 37.00, 'delivered', now() - interval '15 days'),
-- Karen Davis
('b0000000-0000-0000-0000-000000000085', 'a0000000-0000-0000-0000-000000000011', 'Straw Boater', 'panama', 'natural', 'M', 1, 76.00, 76.00, 'delivered', now() - interval '68 days'),
('b0000000-0000-0000-0000-000000000086', 'a0000000-0000-0000-0000-000000000011', 'Fleece Headband Beanie', 'beanie', 'coral', 'S', 1, 22.00, 22.00, 'delivered', now() - interval '3 days'),
-- Leo Nguyen
('b0000000-0000-0000-0000-000000000087', 'a0000000-0000-0000-0000-000000000012', 'Graphic Snapback', 'snapback', 'black/gold', 'M', 1, 39.00, 39.00, 'delivered', now() - interval '4 days'),
('b0000000-0000-0000-0000-000000000088', 'a0000000-0000-0000-0000-000000000012', 'Sherpa Cowboy Hat', 'cowboy', 'suede brown', 'L', 1, 138.00, 138.00, 'cancelled', now() - interval '30 days'),
-- Mia Garcia
('b0000000-0000-0000-0000-000000000089', 'a0000000-0000-0000-0000-000000000013', 'Linen Bucket Hat', 'bucket', 'sage', 'S', 1, 43.00, 43.00, 'delivered', now() - interval '2 days'),
('b0000000-0000-0000-0000-000000000090', 'a0000000-0000-0000-0000-000000000013', 'Wool Beret Classic', 'beret', 'red', 'M', 1, 50.00, 50.00, 'delivered', now() - interval '52 days'),
-- Noah Brown
('b0000000-0000-0000-0000-000000000091', 'a0000000-0000-0000-0000-000000000014', 'Performance Trucker', 'trucker', 'black/red', 'L', 1, 31.00, 31.00, 'delivered', now() - interval '37 days'),
('b0000000-0000-0000-0000-000000000092', 'a0000000-0000-0000-0000-000000000014', 'Knit Slouch Beanie', 'beanie', 'oatmeal', 'M', 1, 26.00, 26.00, 'delivered', now() - interval '12 days'),
-- Olivia Taylor
('b0000000-0000-0000-0000-000000000093', 'a0000000-0000-0000-0000-000000000015', 'Vintage Cowboy Hat', 'cowboy', 'distressed brown', 'M', 1, 118.00, 118.00, 'delivered', now() - interval '82 days'),
('b0000000-0000-0000-0000-000000000094', 'a0000000-0000-0000-0000-000000000015', 'Packable Panama', 'panama', 'olive', 'S', 1, 64.00, 64.00, 'delivered', now() - interval '24 days'),
-- Peter Singh
('b0000000-0000-0000-0000-000000000095', 'a0000000-0000-0000-0000-000000000016', 'Bamboo Fedora', 'fedora', 'natural', 'M', 1, 88.00, 88.00, 'delivered', now() - interval '41 days'),
('b0000000-0000-0000-0000-000000000096', 'a0000000-0000-0000-0000-000000000016', 'Patchwork Bucket', 'bucket', 'multi', 'L', 1, 47.00, 47.00, 'delivered', now() - interval '19 days'),
-- Quinn Adams
('b0000000-0000-0000-0000-000000000097', 'a0000000-0000-0000-0000-000000000017', 'Leather Cowboy Deluxe', 'cowboy', 'black', 'XL', 1, 160.00, 160.00, 'delivered', now() - interval '56 days'),
('b0000000-0000-0000-0000-000000000098', 'a0000000-0000-0000-0000-000000000017', 'Striped Beanie', 'beanie', 'navy/white', 'M', 1, 24.00, 24.00, 'delivered', now() - interval '8 days'),
-- Rachel Moore
('b0000000-0000-0000-0000-000000000099', 'a0000000-0000-0000-0000-000000000018', 'Silk-Lined Fedora', 'fedora', 'burgundy', 'S', 1, 102.00, 102.00, 'shipped', now() - interval '5 days'),
-- Sam Cooper
('b0000000-0000-0000-0000-000000000100', 'a0000000-0000-0000-0000-000000000019', 'Custom Team Snapback', 'custom', 'team colors', 'M', 5, 40.00, 200.00, 'delivered', now() - interval '18 days');

-- ============================================================
-- SUPPORT TICKETS (15 total)
-- Mix of categories, statuses, and priorities
-- ============================================================
insert into support_tickets (id, customer_id, order_id, subject, description, category, status, priority, created_at) values
-- Billing tickets
('c0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001', 'b0000000-0000-0000-0000-000000000002', 'Double charged for Panama hat', 'I was charged twice for my Summer Straw Panama order. Please refund the duplicate charge of $75.00.', 'billing', 'open', 'high', now() - interval '2 days'),
('c0000000-0000-0000-0000-000000000004', 'a0000000-0000-0000-0000-000000000004', 'b0000000-0000-0000-0000-000000000004', 'Wrong amount charged', 'I ordered 2 snapbacks at $34.99 each but was charged $74.98 instead of $69.98.', 'billing', 'open', 'medium', now() - interval '5 days'),
('c0000000-0000-0000-0000-000000000010', 'a0000000-0000-0000-0000-000000000012', null, 'Missing loyalty discount', 'I should have received a 10% discount on my last order but it was not applied.', 'billing', 'in_progress', 'medium', now() - interval '8 days'),

-- Order tickets
('c0000000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-000000000005', 'b0000000-0000-0000-0000-000000000022', 'Order still not shipped', 'My Festival Snapback order from 4 days ago still shows as shipped but no tracking update. When will it arrive?', 'order', 'open', 'medium', now() - interval '1 day'),
('c0000000-0000-0000-0000-000000000005', 'a0000000-0000-0000-0000-000000000010', 'b0000000-0000-0000-0000-000000000035', 'Where is my order?', 'My Fleece Beanie was shipped 3 days ago but I have no tracking information.', 'order', 'open', 'low', now() - interval '1 day'),
('c0000000-0000-0000-0000-000000000011', 'a0000000-0000-0000-0000-000000000016', 'b0000000-0000-0000-0000-000000000053', 'Shipping delay concern', 'My Fitted Snapback has been in shipped status for days with no movement.', 'order', 'in_progress', 'low', now() - interval '2 days'),

-- Product tickets
('c0000000-0000-0000-0000-000000000003', 'a0000000-0000-0000-0000-000000000006', 'b0000000-0000-0000-0000-000000000023', 'Hat arrived damaged', 'My Irish Tweed Flat Cap arrived with a tear on the brim. I need a replacement or refund.', 'product', 'escalated', 'high', now() - interval '3 days'),
('c0000000-0000-0000-0000-000000000006', 'a0000000-0000-0000-0000-000000000011', 'b0000000-0000-0000-0000-000000000039', 'Wrong color received', 'I ordered pink Pom-Pom Beanies but received purple ones.', 'product', 'open', 'high', now() - interval '1 day'),
('c0000000-0000-0000-0000-000000000012', 'a0000000-0000-0000-0000-000000000014', 'b0000000-0000-0000-0000-000000000046', 'Size runs small', 'The Mesh Trucker Caps I received are much smaller than expected for a Large.', 'product', 'open', 'medium', now() - interval '4 days'),

-- Return tickets
('c0000000-0000-0000-0000-000000000007', 'a0000000-0000-0000-0000-000000000009', 'b0000000-0000-0000-0000-000000000007', 'Want to return bucket hat', 'The Outdoor Bucket Hat does not fit well. I would like to return it.', 'return', 'open', 'low', now() - interval '2 days'),
('c0000000-0000-0000-0000-000000000008', 'a0000000-0000-0000-0000-000000000013', 'b0000000-0000-0000-0000-000000000043', 'Return request for sun hat', 'I would like to return the Raffia Sun Hat, it does not match my outfit as expected.', 'return', 'resolved', 'low', now() - interval '6 days'),

-- Other / escalated tickets
('c0000000-0000-0000-0000-000000000009', 'a0000000-0000-0000-0000-000000000008', null, 'Membership tier upgrade request', 'I have been a loyal customer and would like to be considered for a gold membership upgrade.', 'other', 'open', 'low', now() - interval '10 days'),
('c0000000-0000-0000-0000-000000000013', 'a0000000-0000-0000-0000-000000000003', null, 'Feedback on new collection', 'I love the new beret collection! Will you be adding more colors for the holiday season?', 'other', 'resolved', 'low', now() - interval '15 days'),
('c0000000-0000-0000-0000-000000000014', 'a0000000-0000-0000-0000-000000000017', 'b0000000-0000-0000-0000-000000000097', 'Complaint about leather quality', 'The leather on my Cowboy Deluxe hat is peeling after just 2 months. This is unacceptable for a $160 hat. I want to speak with a manager.', 'product', 'escalated', 'high', now() - interval '1 day'),
('c0000000-0000-0000-0000-000000000015', 'a0000000-0000-0000-0000-000000000019', 'b0000000-0000-0000-0000-000000000100', 'Custom order issue', 'The custom team snapbacks have the logo slightly off-center. Need to discuss options.', 'product', 'in_progress', 'high', now() - interval '3 days');
