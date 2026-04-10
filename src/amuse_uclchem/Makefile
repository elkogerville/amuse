ifneq (,$(filter-out clean distclean, $(MAKECMDGOALS)))
include support/config.mk
endif

# Detecting dependencies
support/config.mk:
	cd support && ./configure

# Downloading the code
VERSION = 4.0.0-rc4

uclchem.tar.gz:
	$(DOWNLOAD) https://github.com/uclchem/uclchem/archive/refs/tags/v$(VERSION).tar.gz >$@

# PATCHES := $(shell cat patches/series)

src/UCLCHEM-$(VERSION): uclchem.tar.gz
	##### Modify as needed #####
	tar xf $<
	mv UCLCHEM-$(VERSION) src/
	##### Apply patches here, if needed #####
	# patch <patch.patch
	# for p in $(PATCHES) ; do patch -p1 <patches/$$p ; done


# Building the code into a static library
##### Remove anything not needed #####
DEPFLAGS += $(STOPCOND_CFLAGS)
# DEPFLAGS += $(FORSOCKETS_CFLAGS) $(SIMPLE_HASH_CFLAGS) $(G6LIB_CFLAGS)
# DEPFLAGS += $(SAPPORO_LIGHT_CFLAGS)

##### Pick whichever language is applicable for the code #####
# DEPFLAGS += $(OPENMP_CFLAGS) $(OPENMP_FFLAGS) $(OPENMP_CXXFLAGS)

# ##### Remove anything not needed #####
# DEPFLAGS += $(CUDA_FLAGS)
# DEPFLAGS += $(CL_CFLAGS)
# ##### LAPACK doesn't have flags, only libs... #####
# DEPFLAGS += $(GSL_FLAGS)
# DEPFLAGS += $(GMP_FLAGS)
# DEPFLAGS += $(MPFR_FLAGS)
# DEPFLAGS += $(FFTW_FLAGS)
# ##### Pick whichever language is applicable for the code #####
# DEPFLAGS += $(HDF5_CFLAGS) $(HDF5_FFLAGS)
# ##### Pick whichever language is applicable for the code #####
# DEPFLAGS += $(NETCDF4_CFLAGS) $(NETCDF4_FFLAGS)

# CFLAGS += $(DEPFLAGS)
FCFLAGS += $(DEPFLAGS)

LDLIBS += -lm $(STOPCOND_LIBS)
#$(STOPCONDMPI_LIBS) $(AMUSE_MPI_LIBS)
# LDLIBS += $(FORSOCKETS_LIBS) $(SIMPLE_HASH_LIBS) $(G6LIB_LIBS)
# LDLIBS += $(SAPPORO_LIGHT_LIBS)

# # TODO CUDA, anything else?
# LDLIBS += $(CL_LIBS)
# LDLIBS += $(LAPACK_LIBS) $(BLAS_LIBS) $(LIBS) $(FLIBS)
# LDLIBS += $(GSL_LIBS)
# LDLIBS += $(GMP_LIBS)
# LDLIBS += $(MPFR_LIBS)
# LDLIBS += $(FFTW_LIBS)
# ##### Pick whichever language is applicable for the code #####
# LDLIBS += $(HDF5_LIBS) $(HDF5_FLIBS)
# ##### Pick whichever language is applicable for the code #####
# LDLIBS += $(NETCDF4_LIBS) $(NETCDF4_FLIBS)


CODELIB = src/UCLCHEM-$(VERSION)/src/fortran_src/libuclchem.a


##### Modify build command as needed ##### FIXME
.PHONY: $(CODELIB)
$(CODELIB): | src/UCLCHEM-$(VERSION)/src/fortran_src
	$(MAKE) -C src -j $(CPU_COUNT) all


# Building the workers
# uclchem_worker.f90: interface.py
# 	amusifier --type=f90 interface.py UclchemInterface -o $@

# uclchem_worker.o: uclchem_worker.f90
# 	$(MPIFC) -c -o $@ $(FCFLAGS) $<

# uclchem_worker: interface.o uclchem_worker.o $(CODELIB)
# 	$(MPIFC) -o $@ $(LDFLAGS) $^ $(LDLIBS)


%.o: %.f90
	$(MPIFC) -o $@ -c $(FCFLAGS) $<


# Which packages contain which workers?
##### Add and/or remove as needed #####
#amuse-uclchem_contains: uclchem_worker
amuse-uclchem_contains: $(CODELIB)

amuse-uclchem-SUFFIX_contains: uclchem_SUFFIX_worker


# Building and installing packages
develop-%: %_contains
	support/shared/uninstall.sh $*
	python -m pip install -e packages/$*

install-%: %_contains
	support/shared/uninstall.sh $*
	python -m pip install packages/$*

package-%: %_contains
	python3 -m pip install -vv --no-cache-dir --no-deps --no-build-isolation --prefix ${PREFIX} packages/$*

test-%:
	cd packages/$* && pytest


# Cleaning up FIXME
.PHONY: clean
clean:
	$(MAKE) -C src clean
	rm -rf *.o *.mod *worker*

.PHONY: distclean
distclean: clean
	rm -f support/config.mk support/config.log support/config.status
	rm -rf support/autom4te.cache
