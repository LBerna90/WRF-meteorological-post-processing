# These are some installation notes taken in the process of installing WRF version 4.7.1 on a computer with Ubuntu 24.04 LTS.

#Install required software
sudo apt-get install build-essential csh gfortran m4
#System environment tests
#A video of this part is available here.
#First and foremost, it is very important to have a gfortran compiler, as well as gcc and cpp. If you have these installed, you should be given a path for the location of each.

which gfortran
/user/bin/gfortran
 which cpp
/user/bin/cpp
 which gcc
/user/bin/gcc
#Check your gcc version. It is recommend using version 4.4.0 or later.

gcc --version
#gcc (Ubuntu 5.3.1−14ubuntu2.1) 5.3.1 20160413
#Copyright (C) 2015 Free Software Foundation, Inc.
#This is free software; see the source for copying conditions. There is NO
#warranty; not even for MERCHANTABILITY of FITNESS FOR A PARTICULAR PURPOSE.
#Create a new, clean directory called Build_WRF, and another one called TESTS.

#There are a few simple tests that can be run to verify that the fortran compiler is built properly, and that it is compatible with the C compiler. Download the tar file that contains the tests into the TESTS directory and unpack the tar file.

 cd {path_to_dir}/TESTS
 wget http://www2.mmm.ucar.edu/wrf/OnLineTutorial/compile_tutorial/tar_files/Fortran_C_tests.tar
 tar -xvf Fortran_C_tests.tar
#There are 7 tests available, so start at the top and run through them, one at a time.

#Test 1: Fixed Format Fortran Test.
 gfortran TEST_1_fortran_only_fixed.f
 ./a.out
#SUCCESS test 1 fortran only fixed format
#Test 2: Free Format Fortran.
 gfortran TEST_2_fortran_only_free.f90
 ./a.out
#Assume Fortran 2003: has FLUSH, ALLOCATABLE, derived type, and ISO C Binding
#SUCCESS test 2 fortran only free format
#Test 3: C.
  gcc TEST_3_c_only.c
 ./a.out
#SUCCESS test 3 c only
#Test 4: Fortran Calling a C Function (our gcc and gfortran have different defaults, so we force both to always use 64 bit [-m64] when combining them).
 gcc -c -m64 TEST_4_fortran+c_c.c
 gfortran -c -m64 TEST_4_fortran+c_f.f90
 gfortran -m64 TEST_4_fortran+c_f.o TEST_4_fortran+c_c.o
 ./a.out
#C function called by Fortran Values are xx = 2.00 and ii = 1
#SUCCESS test 4 fortran calling c

#In addition to the compilers required to manufacture the WRF executables, the WRF build system has scripts as the top level for the user interface. The WRF scripting system uses, and therefore is necessary having csh, perl and sh. To test whether these scripting languages are working properly on the system, there are 3 tests to run. These tests were included in the "Fortran and C Tests Tar File".

#Test 5: csh.
 csh ./TEST_csh.csh
#SUCCESS csh test
#Test 6: perl.
./TEST_perl.pl
#SUCCESS perl test
#Test 7: sh.
 ./TEST_sh.sh
#SUCCESS sh test
#Building libraries
#A video of this part is available here.
#Before getting started, you need to make another directory. Go inside your Build_WRF directory and then make a directory called LIBRARIES.

 cd {path_to_dir}/Build_WRF
 mkdir LIBRARIES
#Depending on the type of run you wish to make, there are various libraries that should be installed. Go inside your LIBRARIES directory and then download all 5 tar files.

 cd {path_to_dir}/Build_WRF/LIBRARIES
 wget http://www2.mmm.ucar.edu/wrf/OnLineTutorial/compile_tutorial/tar_files/mpich-4.3.2.tar.gz http://www2.mmm.ucar.edu/wrf/OnLineTutorial/compile_tutorial/tar_files/netcdf-4.1.3.tar.gz http://www2.mmm.ucar.edu/wrf/OnLineTutorial/compile_tutorial/tar_files/jasper-1.900.1.tar.gz http://www2.mmm.ucar.edu/wrf/OnLineTutorial/compile_tutorial/tar_files/libpng-1.2.50.tar.gz http://www2.mmm.ucar.edu/wrf/OnLineTutorial/compile_tutorial/tar_files/zlib-1.2.7.tar.gz
#It is important to note that these libraries must all be installed with the same compilers as will be used to install WRFV4.5.2 and WPS.

#Configuring NetCDF library: This library is always necessary! Modify the .bashrc file in the home directory of current user to set the environment variables.

 sudo gedit ~/.bashrc
#At the bottom of the file add these lines so that they will be set for future logins.

(...)
export DIR=/home/home/user/BUILD_WRF/LIBRARIES
export CC=gcc
export CXX=g++
export FC=gfortran
export FCFLAGS=-m64
export F77=gfortran
export FFLAGS=-m64

#Then source the file to make these settings active for current session.

 source ~/.bashrc
#Unpack the netcdf-4.1.3.tar.gz file.

 tar -zxvf netcdf-4.1.3.tar.gz
#Go into the netcdf-4.1.3 directory and run the configure script with the parameters presented below, make and make install.

 cd {path_to_dir}/BUILD_WRF/LIBRARIES/netcdf-4.1.3
 ./configure --prefix=$DIR/netcdf --disable-dap --disable-netcdf-4 --disable-shared
 make
 make install
#Modify again the .bashrc file and set two new environment variables at the bottom. Then source the file to make these settings active for current session and leave the directory.

$ sudo gedit ~/.bashrc

(...)
export PATH=$DIR/netcdf/bin:$PATH
export NETCDF=$DIR/netcdf

$ source ~/.bashrc
$ cd ..
#Configuring MPICH library: This library is necessary if you are planning to build WRF in parallel. If your machine does not have more than 1 processor, or if you have no need to run WRF with multiple processors, you can skip installing MPICH.

#In principle, any implementation of the MPI-2 standard should work with WRF; however, we have the most experience with MPICH, and therefore, that is what will be described here.

#Assuming all the export commands were already issued while setting up NetCDF, you can continue on to install MPICH, issuing each of the following commands.

 cd {path_to_dir}/Build_WRF/LIBRARIES
 tar -zxvf mpich-4.3.2.tar.gz
 cd {path_to_dir}/Build_WRF/LIBRARIES/mpich-4.3.2
./configure --prefix=$DIR/mpich --with-device=ch4:ofi FFLAGS="-fallow-argument-mismatch" FCFLAGS="-fallow-argument-mismatch"
 make
 make install
 sudo gedit ~/.bashrc

(...)
export PATH=$DIR/mpich/bin:$PATH

 source ~/.bashrc
 cd ..
#Configuring zlib: This is a compression library necessary for compiling WPS (specifically ungrib) with GRIB2 capability. Assuming all the export commands from the NetCDF install are already set, you can move on to the commands to install zlib.

 cd {path_to_dir}/Build_WRF/LIBRARIES
 sudo gedit ~/.bashrc

(...)
export LDFLAGS=-L$DIR/grib2/lib 
export CPPFLAGS=-I$DIR/grib2/include 

 source ~/.bashrc
 tar -zxvf zlib-1.2.7.tar.gz
 cd {path_to_dir}/Build_WRF/LIBRARIES/zlib-1.2.7
 ./configure --prefix=$DIR/grib2
 make
 make install
 cd ..
#Configuring libpng: This is a compression library necessary for compiling WPS (specifically ungrib) with GRIB2 capability. Assuming all the export commands from the NetCDF install are already set, you can move on to the commands to install libpng.

 cd {path_to_dir}/Build_WRF/LIBRARIES
 tar -zxvf libpng-1.2.50.tar.gz
 cd {path_to_dir}/Build_WRF/LIBRARIES/libpng-1.2.50
 ./configure --prefix=$DIR/grib2
 make
 make install
 cd ..
#Configuring JasPer: This is a compression library necessary for compiling WPS (specifically ungrib) with GRIB2 capability. Assuming all the export commands from the NetCDF install are already set, you can move on to the commands to install jasper.

 cd {path_to_dir}/Build_WRF/LIBRARIES
 tar -zxvf jasper-1.900.1.tar.gz
 cd {path_to_dir}/Build_WRF/LIBRARIES/jasper-1.900.1
 ./configure --prefix=$DIR/grib2
 make
 make install
 export LD_LIBRARY_PATH=/home/user/BUILD_WRF/LIBRARIES/grib2/lib:$LD_LIBRARY_PATH
 cd ..
#Libraries compatibility tests
#A video of this part is available here.
#Once the target machine is able to make small Fortran and C executables (what was verified in the System Environment Tests section), and after the NetCDF and MPI libraries are constructed (two of the libraries from the Building Libraries section), to emulate the WRF codes behavior, two additional small tests are required. We need to verify that the libraries are able to work with the compilers that are to be used for the WPS and WRF builds.

 cd {path_to_dir}/Build_WRF
 mkdir WRF
 cd WRF
 wget https://github.com/wrf-model/WRF/releases/download/v4.7.1/v4.7.1.tar.gz
 tar -zxvf v4.7.1.tar.gz
 ./configure

#You will see various options. Choose the option that lists the compiler you are using and the way you wish to build WRFV3 (i.e., serially or in parallel). Although there are 3 different types of parallel (smpar, dmpar, and dm+sm), it is recommend choosing dmpar option.

#checking for perl5... no
#checking for perl... found /usr/bin/perl (perl)
#Will use NETCDF in dir: /usr
#HDF5 not set in environment. Will configure WRF for use without.
#PHDF5 not set in environment. Will configure WRF for use without.
#Will use 'time' to report timing information
#$JASPERLIB or $JASPERINC not found in environment, configuring to build without grib2 I/O...
#-----------------------------------------------------------------------------------------------

#Please select from among the following Linux x86_64 options: 
35

-----------------------------------------------------------------------------------------------
Compile for nesting? (1=basic, 2=preset moves, 3=vortex following) [default 1]: 1

Configuration successful!
-----------------------------------------------------------------------------------------------
testing for MPI_Comm_f2c and MPI_Comm_c2f 
	MPI_Comm_f2c and MPI_Comm_c2f are supported
testing for fseeko and fseeko64
fseeko64 is supported
-----------------------------------------------------------------------------------------------

(...)
Once your configuration is complete, you should have a configure.wrf file, and you are ready to compile. To compile WRFV3, you will need to decide which type of case you wish to compile. The options are listed below.

em_real (3d real case)
em_quarter_ss (3d ideal case)
em_b_wave (3d ideal case)
em_les (3d ideal case)
em_heldsuarez (3d ideal case)
em_tropical_cyclone (3d ideal case)
em_hill2d_x (2d ideal case)
em_squall2d_x (2d ideal case)
em_squall2d_y (2d ideal case)
em_grav2d_x (2d ideal case)
em_seabreeze2d_x (2d ideal case)
em_scm_xy (1d ideal case)
For this purpose we are going to compile WRF for real cases. Compilation should take about 20-30 minutes. The ongoing compilation can be checked.

./compile em_real 
 
 >& compile.log &
 tail -f compile.log
Once the compilation completes, to check whether it was successful, you need to look for executables in the WRFV3/main directory.

 ls -las main/*.exe
ndown.exe (one-way nesting)
real.exe (real data initialization)
tc.exe (for tc bogusing--serial only)
wrf.exe (model executable)
These executables are linked to 2 different directories. You can choose to run WRF from either directory.
mkdir WPS
export WPS_GEOG=/home/user/BUILD_WRF/WPS

#Building WPS

After the WRF model is built, the next step is building the WPS program (if you plan to run real cases, as opposed to idealized cases)). The WRF model MUST be properly built prior to trying to build the WPS programs. If you do not already have the WPS source code, move to your Build_WRF directory, download that file and unpack it. Then go into the WPS directory and make sure the WPS directory is clean.

 cd {path_to_dir}/Build_WRF
 wget https://github.com/wrf-model/WPS/archive/refs/tags/v4.5.tar.gz
 tar -zxvf WPS-4.5.tar.gz
 cd {path_to_dir}/Build_WRF/WPS
 ./clean
The next step is to configure WPS, however, you first need to set some paths for the ungrib libraries and then you can configure.

 sudo gedit ~/.bashrc

(...)
export JASPERLIB=$DIR/grib2/lib
export JASPERINC=$DIR/grib2/include

 source ~/.bashrc
 ./configure
 
You should be given a list of various options for compiler types, whether to compile in serial or parallel, and whether to compile ungrib with GRIB2 capability. Unless you plan to create extremely large domains, it is recommended to compile WPS in serial mode, regardless of whether you compiled WRFV3 in parallel. It is also recommended that you choose a GRIB2 option (make sure you do not choose one that states "NO_GRIB2"). You may choose a non-grib2 option, but most data is now in grib2 format, so it is best to choose this option. You can still run grib1 data when you have built with grib2.

Choose the option that lists a compiler to match what you used to compile WRFV3, serial, and grib2. Note: The option number will likely be different than the number you chose to compile WRF.

Will use NETCDF in dir: /home/modelagem/Build_WRF/LIBRARIES/netcdf
Found Jasper environment variables for GRIB2 support...
  $JASPERLIB = /home/modelagem/Build_WRF/LIBRARIES/grib2/lib
  $JASPERINC = /home/modelagem/Build_WRF/LIBRARIES/grib2/include
-----------------------------------------------------------------------------------------------
Please select from among the following supported platforms:

   1. Linux x86_64, gfortran (serial)
   2. Linux x86_64, gfortran (serial_NO_GRIB2)
   3. Linux x86_64, gfortran (dmpar)
   4. Linux x86_64, gfortran (dmpar_NO_GRIB2)
   5. Linux x86_64, PGI compiler (serial)
   6. Linux x86_64, PGI compiler (serial_NO_GRIB2)
   7. Linux x86_64, PGI compiler (dmpar)
   8. Linux x86_64, PGI compiler (dmpar_NO_GRIB2)
   9. Linux x86_64, PGI compiler, SGI MPT (serial)
  10. Linux x86_64, PGI compiler, SGI MPT (serial_NO_GRIB2)
  11. Linux x86_64, PGI compiler, SGI MPT (dmpar)
  12. Linux x86_64, PGI compiler, SGI MPT (dmpar_NO_GRIB2)
  13. Linux x86_64, IA64 and Opteron (serial)
  14. Linux x86_64, IA64 and Opteron (serial_NO_GRIB2)
  15. Linux x86_64, IA64 and Opteron (dmpar)
  16. Linux x86_64, IA64 and Opteron (dmpar_NO_GRIB2)
  17. Linux x86_64, Intel compiler (serial)
  18. Linux x86_64, Intel compiler (serial_NO_GRIB2)
  19. Linux x86_64, Intel compiler (dmpar)
  20. Linux x86_64, Intel compiler (dmpar_NO_GRIB2)
  21. Linux x86_64, Intel compiler, SGI MPT (serial)
  22. Linux x86_64, Intel compiler, SGI MPT (serial_NO_GRIB2)
  23. Linux x86_64, Intel compiler, SGI MPT (dmpar)
  24. Linux x86_64, Intel compiler, SGI MPT (dmpar_NO_GRIB2)
  25. Linux x86_64, Intel compiler, IBM POE (serial)
  26. Linux x86_64, Intel compiler, IBM POE (serial_NO_GRIB2)
  27. Linux x86_64, Intel compiler, IBM POE (dmpar)
  28. Linux x86_64, Intel compiler, IBM POE (dmpar_NO_GRIB2)
  29. Linux x86_64 g95 compiler (serial)
  30. Linux x86_64 g95 compiler (serial_NO_GRIB2)
  31. Linux x86_64 g95 compiler (dmpar)
  32. Linux x86_64 g95 compiler (dmpar_NO_GRIB2)
  33. Cray XE/XC CLE/Linux x86_64, Cray compiler (serial)
  34. Cray XE/XC CLE/Linux x86_64, Cray compiler (serial_NO_GRIB2)
  35. Cray XE/XC CLE/Linux x86_64, Cray compiler (dmpar)
  36. Cray XE/XC CLE/Linux x86_64, Cray compiler (dmpar_NO_GRIB2)
  37. Cray XC CLE/Linux x86_64, Intel compiler (serial)
  38. Cray XC CLE/Linux x86_64, Intel compiler (serial_NO_GRIB2)
  39. Cratail -f compile.logy XC CLE/Linux x86_64, Intel compiler (dmpar)
  40. Cray XC CLE/Linux x86_64, Intel compiler (dmpar_NO_GRIB2)

Enter selection [1-40] : 3
-----------------------------------------------------------------------------------------------
Configuration successful. To build the WPS, type: compile
-----------------------------------------------------------------------------------------------
The metgrid.exe and geogrid.exe programs rely on the WRF model's I/O libraries. There is a line in the configure.wps file that directs the WPS build system to the location of the I/O libraries from the WRF model.

(...)
WRF_DIR = ../WRF
(...)
Above is the default setting. As long as the name of the WRF models top-level directory is "WRF" and the WPS and WRFV3 directories are at the same level (which they should be if you have followed exactly as instructed on this page so far), then the existing default setting is correct and there is no need to change it. If it is not correct, you must modify the configure file and then save the changes before compiling.

You can now compile WPS. Compilation should take a few minutes. The ongoing compilation can be checked.

$ ./compile >& compile.log

$ tail -f compile.log &

Once the compilation completes, to check whether it was successful, you need to look for 3 main executables in the WPS top-level directory. Then verify that they are not zero-sized.

$ ls -ls *.exe
geogrid.exe
metgrid.exe
ungrib.exe



#===================================================================#

#Static geography data

#The WRF modeling system is able to create idealized simulations, though most users are interested in the real-data cases. To initiate a real-data case, the domains physical location on the globe and the static information for that location must be created. This requires a data set that includes such fields as topography and land use categories. Move to your Build_WRF directory, download the file and unpack it. Once unpacked it will be called geog, rename to WPS_GEOG.

cd {path_to_dir}/Build_WRF
wget https://www2.mmm.ucar.edu/wrf/src/wps_files/geog_high_res_mandatory.tar.gz
tar -xvf geog_high_res_mandatory.tar.gz
mv geog WPS_GEOG


cd WPS
gedit namelist.wps

(...)
geog_data_path = '{path_to_dir}/Build_WRF/WPS_GEOG'
(...)



