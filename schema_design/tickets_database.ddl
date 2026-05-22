CREATE SCHEMA IF NOT EXISTS content;

CREATE TABLE content.event (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    event_date TIMESTAMP WITH TIME ZONE NOT NULL,
    venue VARCHAR(255) NOT NULL,
    description TEXT,
    created TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    modified TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE content.ticket_tier (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID NOT NULL REFERENCES content.event(id) ON DELETE CASCADE,
    name VARCHAR(50) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    total_capacity INT NOT NULL,
    available_quantity INT NOT NULL,
    created TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    modified TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (event_id, name)
);

CREATE TABLE content.reservation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_tier_id UUID NOT NULL REFERENCES content.ticket_tier(id) ON DELETE RESTRICT,
    customer_name VARCHAR(255) NOT NULL,
    customer_email VARCHAR(255) NOT NULL,
    quantity_bought INT NOT NULL,
    status VARCHAR(50) DEFAULT 'confirmed',
    reservation_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX event_date_idx ON content.event(event_date);
CREATE INDEX tier_availability_idx ON content.ticket_tier(available_quantity);