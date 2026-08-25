-- create processing schema 
create SCHEMA airbnb_db.processing; 

grant USAGE on SCHEMA airbnb_db.processing to ROLE data_engineer; 

-- CALENDAR 
-- review raw calendar data
select * 
from airbnb_db.raw.calendar
limit 10; 

-- create processing calendar table 
create or replace TABLE airbnb_db.processing.calendar_proc
    CLONE airbnb_db.raw.calendar; 

-- review processing calendar table 
select * 
from airbnb_db.processing.calendar_proc
limit 10; 

-- LISTINGS 
-- review raw listings data
select * 
from airbnb_db.raw.listings
limit 10; 

-- create processing listings table 
create or replace TABLE airbnb_db.processing.listings_proc
    CLONE airbnb_db.raw.listings; 

-- review processing listings table 
select * 
from airbnb_db.processing.listings_proc
limit 10; 


-- REVIEWS 
-- review raw reviews data
select * 
from airbnb_db.raw.reviews
limit 10; 

-- create processing reviews table 
create or replace TABLE airbnb_db.processing.reviews_proc
    CLONE airbnb_db.raw.reviews; 

-- review processing reviews table 
select * 
from airbnb_db.processing.reviews_proc
limit 10; 