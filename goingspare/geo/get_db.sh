rm -f GeoIP.dat.gz GeoLiteCity.dat.gz
wget http://geolite.maxmind.com/download/geoip/database/GeoLiteCountry/GeoIP.dat.gz
wget http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz
gunzip GeoIP.dat.gz
gunzip GeoLiteCity.dat.gz

# Outcode data for turning postcodes in scraped offer descriptions into lat/lng
# wget http://www.freemaptools.com/download/postcodes/postcodes.csv
# This needs to be run as the postgres user
# cat postcodes.csv | psql goingspare -c "COPY geo_outcode(id,outcode,lat,lng) FROM STDIN WITH CSV HEADER;"
