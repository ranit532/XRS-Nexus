import sqlite3
import faker
import random
import os
from datetime import datetime, timedelta

# Initialize Faker
fake = faker.Faker()
Faker_Seed = 42
fake.seed_instance(Faker_Seed)
random.seed(Faker_Seed)

DB_PATH = "data/complex_erp.db"

def create_connection():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    return conn

def create_schema(conn):
    cursor = conn.cursor()
    
    # --- HR Schema (5 tables) ---
    cursor.execute('''CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY,
        name TEXT,
        location TEXT,
        budget REAL
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS roles (
        id INTEGER PRIMARY KEY,
        title TEXT,
        min_salary REAL,
        max_salary REAL
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        email TEXT,
        phone TEXT,
        hire_date DATE,
        dept_id INTEGER,
        role_id INTEGER,
        FOREIGN KEY (dept_id) REFERENCES departments (id),
        FOREIGN KEY (role_id) REFERENCES roles (id)
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS salaries (
        id INTEGER PRIMARY KEY,
        emp_id INTEGER,
        amount REAL,
        effective_date DATE,
        FOREIGN KEY (emp_id) REFERENCES employees (id)
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS performance_reviews (
        id INTEGER PRIMARY KEY,
        emp_id INTEGER,
        review_date DATE,
        rating INTEGER,
        comments TEXT,
        FOREIGN KEY (emp_id) REFERENCES employees (id)
    )''')

    # --- Product & Inventory (6 tables) ---
    cursor.execute('''CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY,
        name TEXT,
        description TEXT
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY,
        name TEXT,
        contact_name TEXT,
        email TEXT,
        country TEXT
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT,
        sku TEXT,
        category_id INTEGER,
        supplier_id INTEGER,
        price REAL,
        cost REAL,
        FOREIGN KEY (category_id) REFERENCES categories (id),
        FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS warehouses (
        id INTEGER PRIMARY KEY,
        name TEXT,
        address TEXT,
        capacity INTEGER
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY,
        product_id INTEGER,
        warehouse_id INTEGER,
        quantity INTEGER,
        last_updated DATE,
        FOREIGN KEY (product_id) REFERENCES products (id),
        FOREIGN KEY (warehouse_id) REFERENCES warehouses (id)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS shipments (
        id INTEGER PRIMARY KEY,
        tracking_number TEXT,
        supplier_id INTEGER,
        warehouse_id INTEGER,
        shipped_date DATE,
        status TEXT,
        FOREIGN KEY (supplier_id) REFERENCES suppliers (id),
        FOREIGN KEY (warehouse_id) REFERENCES warehouses (id)
    )''')

    # --- Sales & CRM (7 tables) ---
    cursor.execute('''CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT,
        phone TEXT,
        address TEXT,
        segment TEXT
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT,
        source TEXT,
        status TEXT,
        created_at DATE
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS opportunities (
        id INTEGER PRIMARY KEY,
        lead_id INTEGER,
        amount REAL,
        stage TEXT,
        close_date DATE,
        FOREIGN KEY (lead_id) REFERENCES leads (id)
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        order_date DATE,
        status TEXT,
        total_amount REAL,
        FOREIGN KEY (customer_id) REFERENCES customers (id)
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY,
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        unit_price REAL,
        FOREIGN KEY (order_id) REFERENCES orders (id),
        FOREIGN KEY (product_id) REFERENCES products (id)
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY,
        order_id INTEGER,
        invoice_date DATE,
        due_date DATE,
        amount_due REAL,
        FOREIGN KEY (order_id) REFERENCES orders (id)
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY,
        invoice_id INTEGER,
        payment_date DATE,
        amount REAL,
        method TEXT,
        FOREIGN KEY (invoice_id) REFERENCES invoices (id)
    )''')

    # --- Support (4 tables) ---
    cursor.execute('''CREATE TABLE IF NOT EXISTS support_tickets (
        id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        subject TEXT,
        status TEXT,
        priority TEXT,
        created_at DATE,
        FOREIGN KEY (customer_id) REFERENCES customers (id)
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS ticket_comments (
        id INTEGER PRIMARY KEY,
        ticket_id INTEGER,
        author_name TEXT,
        comment_text TEXT,
        created_at DATE,
        FOREIGN KEY (ticket_id) REFERENCES support_tickets (id)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS faqs (
        id INTEGER PRIMARY KEY,
        question TEXT,
        answer TEXT,
        category TEXT
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS customer_feedback (
        id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        ticket_id INTEGER,
        rating INTEGER,
        comments TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers (id),
        FOREIGN KEY (ticket_id) REFERENCES support_tickets (id)
    )''')

    # --- Marketing (3 tables) ---
    cursor.execute('''CREATE TABLE IF NOT EXISTS campaigns (
        id INTEGER PRIMARY KEY,
        name TEXT,
        start_date DATE,
        end_date DATE,
        budget REAL
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS channels (
        id INTEGER PRIMARY KEY,
        name TEXT,
        type TEXT
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS campaign_channels (
        campaign_id INTEGER,
        channel_id INTEGER,
        spend REAL,
        PRIMARY KEY (campaign_id, channel_id),
        FOREIGN KEY (campaign_id) REFERENCES campaigns (id),
        FOREIGN KEY (channel_id) REFERENCES channels (id)
    )''')

    # --- ORPHAN TABLES (5 tables) ---
    # These tables have NO foreign keys to the rest of the system
    cursor.execute('''CREATE TABLE IF NOT EXISTS legacy_users (
        user_id TEXT PRIMARY KEY,
        username TEXT,
        old_password_hash TEXT,
        last_login DATE
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS archived_logs_2020 (
        log_id INTEGER PRIMARY KEY,
        timestamp DATE,
        level TEXT,
        message TEXT,
        module TEXT
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS temp_import_csv (
        row_id INTEGER PRIMARY KEY,
        raw_data TEXT,
        import_status TEXT
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS old_discounts (
        code TEXT PRIMARY KEY,
        percentage REAL,
        expiry_date DATE
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS beta_features_signup (
        email TEXT PRIMARY KEY,
        signup_date DATE,
        preference TEXT
    )''')

    conn.commit()
    print("Schema created successfully (30 tables total).")

def generate_data(conn):
    cursor = conn.cursor()
    
    # 1. Departments
    depts = ['Engineering', 'Sales', 'Marketing', 'HR', 'Finance', 'Support', 'Product', 'Legal']
    for d in depts:
        cursor.execute("INSERT INTO departments (name, location, budget) VALUES (?, ?, ?)",
                       (d, fake.city(), random.randint(100000, 1000000)))
    conn.commit()
    
    # 2. Roles
    roles = ['Manager', 'Associate', 'Senior', 'Director', 'Intern']
    for r in roles:
        cursor.execute("INSERT INTO roles (title, min_salary, max_salary) VALUES (?, ?, ?)",
                       (r, 40000, 150000))
    conn.commit()
    
    # 3. Employees
    dept_ids = [row[0] for row in cursor.execute("SELECT id FROM departments").fetchall()]
    role_ids = [row[0] for row in cursor.execute("SELECT id FROM roles").fetchall()]
    
    for _ in range(50):
        cursor.execute('''INSERT INTO employees (first_name, last_name, email, phone, hire_date, dept_id, role_id)
                          VALUES (?, ?, ?, ?, ?, ?, ?)''',
                       (fake.first_name(), fake.last_name(), fake.email(), fake.phone_number(), fake.date_this_decade(),
                        random.choice(dept_ids), random.choice(role_ids)))
    conn.commit()
    emp_ids = [row[0] for row in cursor.execute("SELECT id FROM employees").fetchall()]

    # 4. Salaries
    for eid in emp_ids:
        cursor.execute("INSERT INTO salaries (emp_id, amount, effective_date) VALUES (?, ?, ?)",
                       (eid, random.uniform(50000, 120000), fake.date_this_year()))
    
    # 5. Performance Reviews
    for eid in emp_ids:
         cursor.execute("INSERT INTO performance_reviews (emp_id, review_date, rating, comments) VALUES (?, ?, ?, ?)",
                       (eid, fake.date_this_year(), random.randint(1, 5), fake.sentence()))
    conn.commit()

    # 6. Categories
    cats = ['Electronics', 'Furniture', 'Office Supplies', 'Software', 'Apparel']
    for c in cats:
        cursor.execute("INSERT INTO categories (name, description) VALUES (?, ?)", (c, fake.sentence()))
    
    # 7. Suppliers
    for _ in range(10):
        cursor.execute("INSERT INTO suppliers (name, contact_name, email, country) VALUES (?, ?, ?, ?)",
                       (fake.company(), fake.name(), fake.company_email(), fake.country()))
    conn.commit()
    
    # 8. Products
    cat_ids = [row[0] for row in cursor.execute("SELECT id FROM categories").fetchall()]
    sup_ids = [row[0] for row in cursor.execute("SELECT id FROM suppliers").fetchall()]
    
    for _ in range(100):
        cursor.execute("INSERT INTO products (name, sku, category_id, supplier_id, price, cost) VALUES (?, ?, ?, ?, ?, ?)",
                       (fake.word().capitalize() + " " + fake.word().capitalize(), fake.ean13(), 
                        random.choice(cat_ids), random.choice(sup_ids), 
                        random.uniform(10, 500), random.uniform(5, 300)))
    conn.commit()
    prod_ids = [row[0] for row in cursor.execute("SELECT id FROM products").fetchall()]

    # 9. Warehouses
    for _ in range(5):
        cursor.execute("INSERT INTO warehouses (name, address, capacity) VALUES (?, ?, ?)",
                       (fake.city() + " DC", fake.address(), random.randint(1000, 10000)))
    conn.commit()
    wh_ids = [row[0] for row in cursor.execute("SELECT id FROM warehouses").fetchall()]

    # 10. Inventory
    for pid in prod_ids:
        for wid in wh_ids:
            if random.random() > 0.5:
                cursor.execute("INSERT INTO inventory (product_id, warehouse_id, quantity, last_updated) VALUES (?, ?, ?, ?)",
                               (pid, wid, random.randint(0, 500), fake.date_this_year()))
    
    # 11. Shipments
    for _ in range(20):
        cursor.execute("INSERT INTO shipments (tracking_number, supplier_id, warehouse_id, shipped_date, status) VALUES (?, ?, ?, ?, ?)",
                       (fake.uuid4(), random.choice(sup_ids), random.choice(wh_ids), fake.date_this_year(), 
                        random.choice(['Shipped', 'Delivered', 'In-Transit'])))
    conn.commit()

    # 12. Customers
    for _ in range(50):
        cursor.execute("INSERT INTO customers (name, email, phone, address, segment) VALUES (?, ?, ?, ?, ?)",
                       (fake.name(), fake.email(), fake.phone_number(), fake.address(), random.choice(['Retail', 'Wholesale', 'Enterprise'])))
    conn.commit()
    cust_ids = [row[0] for row in cursor.execute("SELECT id FROM customers").fetchall()]
    
    # 13. Leads
    for _ in range(50):
        cursor.execute("INSERT INTO leads (name, email, source, status, created_at) VALUES (?, ?, ?, ?, ?)",
                       (fake.name(), fake.email(), random.choice(['Web', 'Referral', 'Ad']), 
                        random.choice(['New', 'Contacted', 'Qualified', 'Lost']), fake.date_this_year()))
    conn.commit()
    lead_ids = [row[0] for row in cursor.execute("SELECT id FROM leads").fetchall()]

    # 14. Opportunities
    for lid in lead_ids:
        if random.random() > 0.7:
             cursor.execute("INSERT INTO opportunities (lead_id, amount, stage, close_date) VALUES (?, ?, ?, ?)",
                            (lid, random.uniform(1000, 50000), random.choice(['Prospecting', 'Negotiation', 'Closed Won', 'Closed Lost']), fake.date_this_year()))
    
    # 15. Orders
    for _ in range(100):
        cursor.execute("INSERT INTO orders (customer_id, order_date, status, total_amount) VALUES (?, ?, ?, ?)",
                       (random.choice(cust_ids), fake.date_this_year(), random.choice(['Pending', 'Shipped', 'Delivered', 'Cancelled']), 0))
    conn.commit()
    order_ids = [row[0] for row in cursor.execute("SELECT id FROM orders").fetchall()]

    # 16. Order Items & Update Order Total
    for oid in order_ids:
        total = 0
        for _ in range(random.randint(1, 5)):
            pid = random.choice(prod_ids)
            qty = random.randint(1, 10)
            price = cursor.execute("SELECT price FROM products WHERE id=?", (pid,)).fetchone()[0]
            cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
                           (oid, pid, qty, price))
            total += qty * price
        cursor.execute("UPDATE orders SET total_amount=? WHERE id=?", (total, oid))

    # 17. Invoices
    for oid in order_ids:
         cursor.execute("INSERT INTO invoices (order_id, invoice_date, due_date, amount_due) VALUES (?, ?, ?, ?)",
                        (oid, fake.date_this_year(), fake.date_this_year(), 0)) # Amount to be updated
    conn.commit()
    inv_ids = [row[0] for row in cursor.execute("SELECT id FROM invoices").fetchall()]
    
    # Update invoice amounts
    for inv_id in inv_ids:
        oid = cursor.execute("SELECT order_id FROM invoices WHERE id=?", (inv_id,)).fetchone()[0]
        amt = cursor.execute("SELECT total_amount FROM orders WHERE id=?", (oid,)).fetchone()[0]
        cursor.execute("UPDATE invoices SET amount_due=? WHERE id=?", (amt, inv_id))

    # 18. Payments
    for inv_id in inv_ids:
        if random.random() > 0.2:
            amt = cursor.execute("SELECT amount_due FROM invoices WHERE id=?", (inv_id,)).fetchone()[0]
            cursor.execute("INSERT INTO payments (invoice_id, payment_date, amount, method) VALUES (?, ?, ?, ?)",
                           (inv_id, fake.date_this_year(), amt, random.choice(['Credit Card', 'Bank Transfer', 'Check'])))

    # 19. Support Tickets
    for _ in range(30):
        cursor.execute("INSERT INTO support_tickets (customer_id, subject, status, priority, created_at) VALUES (?, ?, ?, ?, ?)",
                       (random.choice(cust_ids), fake.sentence(), random.choice(['Open', 'Closed', 'Pending']), 
                        random.choice(['Low', 'Medium', 'High']), fake.date_this_year()))
    conn.commit()
    ticket_ids = [row[0] for row in cursor.execute("SELECT id FROM support_tickets").fetchall()]

    # 20. Ticket Comments
    for tid in ticket_ids:
        for _ in range(random.randint(1, 3)):
            cursor.execute("INSERT INTO ticket_comments (ticket_id, author_name, comment_text, created_at) VALUES (?, ?, ?, ?)",
                           (tid, fake.name(), fake.sentence(), fake.date_this_year()))

    # 21. FAQs
    for _ in range(10):
        cursor.execute("INSERT INTO faqs (question, answer, category) VALUES (?, ?, ?)",
                       (fake.sentence() + "?", fake.paragraph(), random.choice(['General', 'Billing', 'Tech Support'])))

    # 22. Customer Feedback
    for tid in ticket_ids:
        if random.random() > 0.5:
             cursor.execute("INSERT INTO customer_feedback (customer_id, ticket_id, rating, comments) VALUES (?, ?, ?, ?)",
                            (cursor.execute("SELECT customer_id FROM support_tickets WHERE id=?", (tid,)).fetchone()[0],
                             tid, random.randint(1, 5), fake.sentence()))

    # 23. Campaigns
    for _ in range(5):
        cursor.execute("INSERT INTO campaigns (name, start_date, end_date, budget) VALUES (?, ?, ?, ?)",
                       (fake.bs().title(), fake.date_this_year(), fake.date_this_year(), random.uniform(10000, 50000)))
    conn.commit()
    camp_ids = [row[0] for row in cursor.execute("SELECT id FROM campaigns").fetchall()]

    # 24. Channels
    for ch in ['Email', 'Social Media', 'TV', 'Radio', 'Print']:
        cursor.execute("INSERT INTO channels (name, type) VALUES (?, ?)", (ch, 'Offline' if ch in ['TV', 'Print'] else 'Online'))
    conn.commit()
    chan_ids = [row[0] for row in cursor.execute("SELECT id FROM channels").fetchall()]

    # 25. Campaign Channels
    for cid in camp_ids:
        for chid in chan_ids:
            if random.random() > 0.5:
                cursor.execute("INSERT INTO campaign_channels (campaign_id, channel_id, spend) VALUES (?, ?, ?)",
                               (cid, chid, random.uniform(500, 5000)))

    # --- ORPHAN DATA GENERATION ---
    print("Generating Orphan Data...")
    
    # 26. Legacy Users
    for _ in range(20):
        cursor.execute("INSERT INTO legacy_users (user_id, username, old_password_hash, last_login) VALUES (?, ?, ?, ?)",
                       (fake.uuid4(), fake.user_name(), fake.sha256(), fake.date_between(start_date='-5y', end_date='-2y')))

    # 27. Archived Logs
    for _ in range(100):
        cursor.execute("INSERT INTO archived_logs_2020 (timestamp, level, message, module) VALUES (?, ?, ?, ?)",
                       (fake.date_time_between(start_date='-4y', end_date='-3y'), 
                        random.choice(['INFO', 'WARN', 'ERROR']), fake.sentence(), random.choice(['Auth', 'Billing', 'Core'])))

    # 28. Temp Import
    for i in range(50):
        cursor.execute("INSERT INTO temp_import_csv (raw_data, import_status) VALUES (?, ?)",
                       (f"{fake.name()},{fake.email()},{fake.city()}", random.choice(['Pending', 'Failed'])))

    # 29. Old Discounts
    for _ in range(10):
        cursor.execute("INSERT INTO old_discounts (code, percentage, expiry_date) VALUES (?, ?, ?)",
                       (fake.lexify(text='??????').upper(), random.uniform(0.1, 0.5), fake.date_between(start_date='-3y', end_date='-1y')))
    
    # 30. Beta Signup
    for _ in range(30):
        cursor.execute("INSERT INTO beta_features_signup (email, signup_date, preference) VALUES (?, ?, ?)",
                       (fake.email(), fake.date_this_year(), random.choice(['Dark Mode', 'New UI', 'API Access'])))

    conn.commit()
    print("Data generation complete.")

if __name__ == "__main__":
    conn = create_connection()
    create_schema(conn)
    generate_data(conn)
    conn.close()
