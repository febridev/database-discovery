ALTER TABLE tmproject MODIFY COLUMN project_number char(25) NOT NULL;
ALTER TABLE tthinstance MODIFY COLUMN connection_name varchar(255) NOT NULL;
ALTER TABLE ttdinstance DROP COLUMN total_disk_gb, DROP COLUMN free_disk_gb;
ALTER TABLE ttdinstance ADD COLUMN reserved_disk_gb float NULL AFTER memory_gb;
