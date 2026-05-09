#!/bin/bash

inputdir=/home/user/BUILD_WRF/DATA
rm -rf $inputdir
mkdir $inputdir

year=
month=
day=
cycle=

for ((i=0; i<=72; i+=3))
do

 ftime=`printf "%03d\n" "${i}"`

 server=https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/
 directory=gfs.${year}${month}${day}/${cycle}/atmos/
 file=gfs.t${cycle}z.pgrb2.0p25.f${ftime}

 url=${server}/${directory}/${file}

 echo $url

 wget -O ${inputdir}/${file} ${url}

done
