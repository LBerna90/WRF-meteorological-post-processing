#Running WPS 
# 1. Define a model coarse domain and any nested domains with geogrid.

cd WPS

rm -f geo_em.d0*.nc geogrid.log
ls -ls geogrid/GEOGRID.TBL

#  lrwxrwxrwx  1         15  GEOGRID.TBL -> GEOGRID.TBL.ARW

./geogrid.exe

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#!  Successful completion of geogrid.        !
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

rm -f GRIBFILE.* FILE:* ungrib.log Vtable
ln -s ungrib/Variable_Tables/Vtable.GFS Vtable

ls -ls

#-rw-r--r-- 1  1957004 geo_em.d01.nc
#-rw-r--r-- 1  4745324 geo_em.d02.nc
#-rw-r--r-- 1    11169 geogrid.log


# 2. Extract meteorological fields from GRIB data sets for the simulation period with ungrib.

rm Vtable
ln -s ungrib/Variable_Tables/Vtable.GFS Vtable

./link_grib.csh /home/berna/BUILD_WRF/DATA/

./ungrib.exe

# 3. Horizontally interpolate meteorological fields to the model domains with metgrid.

./metgrid.exe

#running WRF
rm ../WRF/test/em_real/met_em.d0*
mv met_em.d0* /home/berna/BUILD_WRF/WRF/test/em_real

cd ..
cd WRF/test/em_real

rm -f wrfinput_d0* wrfbdy_d01
rm -f rsl.out.* rsl.error.*

./real.exe

export OMP_NUM_THREADS=1

mpirun -np 8 ./wrf.exe




