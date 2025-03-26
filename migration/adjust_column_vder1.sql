--1 DONE
--add column is_deleted in table tthdatabase, flag deleted
ALTER TABLE tthdatabase
ADD COLUMN is_deleted TINYINT DEFAULT 0 COMMENT '0 = available in cloudsql, 1 = deleted in cloudsql' AFTER database_name;


--2 DONE
--adjust length in column database_name
ALTER TABLE tthdatabase 
MODIFY COLUMN database_name VARCHAR(100);	


--3 DONE
--adjust column is_replica in table tthinstance,
    --  existing | 0 = master , 1 = replica
    --  adjust   | 0 = master , 1 = master have replica , 2 = replica
        --  action
        -- select dulu master yang punya replica
        -- select dulu master yang ga punya replica (master only)    
        --  update value 1 replace to 2
        --  value 0 yang master punya replica, di update menjadi 1.

    -- notes : dari code mas feb scrape instance table tthinstance, perlu penyesuaian juga, 
    -- jika replica akan insert value 2 (sebelumnya 1), 
    -- master tetap 0, 
    -- jika master punya replica, harus update manual ke db ubah 0 jadi 1  

--4 DONE
--adjust column database_size_gb to database_size_mb
ALTER TABLE ttddatabase RENAME COLUMN database_size_gb TO database_size_mb;


--5 DONE
--adjust column is_deleted in table tthtable_discovery
ALTER TABLE tthtable_discovery
ADD COLUMN is_deleted TINYINT DEFAULT 0 COMMENT '0 = available in database, 1 = deleted in database' AFTER table_name;


--6 DONE
--adjust add column name `schema_name` in table `tthtable_discovery`
ALTER TABLE `tthtable_discovery`
ADD COLUMN `schema_name` VARCHAR(50) NULL COMMENT 'nama schema'
after h_database_id;

---------------------
--7 DONE
-- adjust flag add column dbdiscovery_on, default 0, 1 = enable , 0 = disable
ALTER TABLE tmproject 
ADD COLUMN full_feature TINYINT DEFAULT 0 COMMENT 'feature database_discovery | 0 = disable, 1 = enable ' AFTER project_name;


--8 DONE
-- adjust add column is_deleted in table tthinstance | default 0, 0 = available in cloudsql, 1 = deleted in cloudsql'
ALTER TABLE tthinstance
ADD COLUMN is_deleted TINYINT DEFAULT 0 COMMENT '0 = available in cloudsql, 1 = deleted in cloudsql' AFTER instance_name;



-- adjust scrape user
-- rename column
alter table ttuser_instance rename column m_instance_id to h_instance_id;

-- add column is_deleted
ALTER TABLE ttuser_instance 
ADD COLUMN is_deleted TINYINT DEFAULT 0 COMMENT '0 = available in database, 1 = deleted in database' AFTER username;

ALTER TABLE ttuser_instance 
ADD COLUMN expired_in SMALLINT COMMENT 'H - Expired' AFTER expired_date;

alter table ttuser_instance rename column expired_stats to status;

ALTER TABLE ttuser_instance 
MODIFY COLUMN privileges text NULL;



--adjust table ttuser
ALTER TABLE ttuser_instance RENAME COLUMN status TO status_user;
ALTER TABLE ttuser_instance MODIFY COLUMN status_user varchar(75) NOT NULL COMMENT 'status user database';

ALTER TABLE ttuser_instance
MODIFY COLUMN expired_date varchar(75) DEFAULT NULL COMMENT 'expired date user database';

ALTER TABLE ttuser_instance modify column username varchar(50) NOT NULL;