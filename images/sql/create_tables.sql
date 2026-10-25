-- Small tables (dimensions)
CREATE TABLE dim_date (
    date_id        NUMBER(8)     PRIMARY KEY,
    full_date      DATE          NOT NULL,
    day_of_month   NUMBER(2),
    month_number   NUMBER(2),
    month_name     VARCHAR2(15),
    weekday        VARCHAR2(15)
);

CREATE TABLE dim_product (
    product_id     NUMBER(3)     PRIMARY KEY,
    product_line   VARCHAR2(40)  NOT NULL
);

CREATE TABLE dim_city (
    city_id        NUMBER(3)     PRIMARY KEY,
    city           VARCHAR2(30)  NOT NULL
);

CREATE TABLE dim_customer (
    customer_id    NUMBER(3)     PRIMARY KEY,
    customer_type  VARCHAR2(15)  NOT NULL,
    gender         VARCHAR2(10)  NOT NULL
);

CREATE TABLE dim_payment (
    payment_id     NUMBER(3)     PRIMARY KEY,
    payment_method VARCHAR2(20)  NOT NULL
);

-- Central table (fact)
CREATE TABLE fact_sales (
    invoice_id     VARCHAR2(20)  PRIMARY KEY,
    date_id        NUMBER(8)     NOT NULL REFERENCES dim_date(date_id),
    product_id     NUMBER(3)     NOT NULL REFERENCES dim_product(product_id),
    city_id        NUMBER(3)     NOT NULL REFERENCES dim_city(city_id),
    customer_id    NUMBER(3)     NOT NULL REFERENCES dim_customer(customer_id),
    payment_id     NUMBER(3)     NOT NULL REFERENCES dim_payment(payment_id),
    unit_price     NUMBER(8,2),
    quantity       NUMBER(3),
    total          NUMBER(10,4),
    rating         NUMBER(3,1)
);