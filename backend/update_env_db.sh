#!/bin/bash
# Update .env to use phishlense_db
sed -i 's/DB_NAME=.*/DB_NAME=phishlense_db/' .env
sed -i 's/DB_USER=.*/DB_USER=phishlense_user/' .env
sed -i 's/DB_PASSWORD=.*/DB_PASSWORD=phishlense_pass123/' .env
echo "✅ Updated .env to use phishlense_db"
