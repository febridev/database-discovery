# How To Run Migration

This is Database For Database Discovery

## Setup MySQL On Docker

Create Network For dba services

```bash
docker network create -d bridge --scope local dba_network
```

Create Directory For Log, Config And Data

```bash
mkdir log
mkdir config
mkdir data
```

Run docker compose to up mysql service on docker

```bash
cd /migrations
docker compose up -d
```

## Database Type

MySQL 8.0+

## Database Client

- MySQL Client
- MySQL Dump

## How To Restore

Login Into Database Create Database

```sql
create database database_discovery;
```

Create Role And Grant Full To Database database discovery

```sql
create role db_database_discovery_so;
grant all privileges on database_discovery.* to db_database_discovery_so;
```

Create user and grant privileges to database_discovery

```sql
create user 'svc_database_discovery_so'@'%' identified by '<password>';
grant db_database_discovery_so to 'svc_database_discovery_so'@'%';

```

Restore Database

```bash
 mysql -u <userdatabase> -p -h <hostdatabase> -P <portdatabase> -f database_discovery < database_discovery.sql

```
