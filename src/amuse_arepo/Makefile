ifneq (,$(filter-out clean distclean, $(MAKECMDGOALS)))
include support/config.mk
endif


# Detecting dependencies
support/config.mk:
	cd support && ./configure


# Downloading the code
VERSION = 1fc135a0244906054c7fd5f667175f63d8d6034b
arepo-$(VERSION).tar.gz:
	$(DOWNLOAD) https://gitlab.mpcdf.mpg.de/vrs/arepo/-/archive/$(VERSION)/arepo-$(VERSION).tar.gz >$@

# PATCHES := $(shell cat patches/series)

src/arepo-$(VERSION): arepo-$(VERSION).tar.gz
	##### Modify as needed #####
	tar xf $<
	mv arepo-$(VERSION) src
	cp src/arepo-$(VERSION)/Template-Config.sh src/arepo-$(VERSION)/Config.sh

	# ##### Apply patches here, if needed #####
	# patch <patch.patch
	# for p in $(PATCHES) ; do patch -p1 <patches/$$p ; done


# Building the code into a static library
##### Remove anything not needed #####
# DEPFLAGS += $(STOPCOND_CFLAGS) $(STOPCONDMPI_CFLAGS) $(AMUSE_MPI_CFLAGS)
# DEPFLAGS += $(SIMPLE_HASH_CFLAGS) $(G6LIB_CFLAGS)
# DEPFLAGS += $(SAPPORO_LIGHT_CFLAGS)

##### Pick whichever language is applicable for the code #####
# DEPFLAGS += $(OPENMP_CFLAGS) $(OPENMP_FFLAGS) $(OPENMP_CXXFLAGS)

##### Remove anything not needed #####
# DEPFLAGS += $(CUDA_FLAGS)
# DEPFLAGS += $(CL_CFLAGS)
##### LAPACK doesn't have flags, only libs... #####
DEPFLAGS += $(GSL_FLAGS)
DEPFLAGS += $(GMP_FLAGS)
# DEPFLAGS += $(MPFR_FLAGS)
DEPFLAGS += $(FFTW_FLAGS)
##### Pick whichever language is applicable for the code #####
DEPFLAGS += $(HDF5_CFLAGS)
##### Pick whichever language is applicable for the code #####
# DEPFLAGS += $(NETCDF4_CFLAGS) $(NETCDF4_FFLAGS)

CFLAGS += $(DEPFLAGS)
CFLAGS += -I src/arepo-$(VERSION)/src
CFLAGS += -I src/arepo-$(VERSION)/build
# LDFLAGS += $(CUDA_LDFLAGS)

# LDLIBS += -lm $(STOPCOND_LIBS) $(STOPCONDMPI_LIBS) $(AMUSE_MPI_LIBS)
# LDLIBS += $(SIMPLE_HASH_LIBS) $(G6LIB_LIBS)
# LDLIBS += $(SAPPORO_LIGHT_LIBS)

# TODO CUDA, anything else?
# LDLIBS += $(CL_LIBS)
# LDLIBS += $(LAPACK_LIBS) $(BLAS_LIBS) $(LIBS) $(FLIBS)
LDLIBS += $(GSL_LIBS)
LDLIBS += $(GMP_LIBS)
# LDLIBS += $(MPFR_LIBS)
LDLIBS += $(FFTW_LIBS)
##### Pick whichever language is applicable for the code #####
LDLIBS += $(HDF5_LIBS) $(HDF5_FLIBS)
LDLIBS += $(shell mpicxx --showme:link)
##### Pick whichever language is applicable for the code #####
# LDLIBS += $(NETCDF4_LIBS) $(NETCDF4_FLIBS)


CODELIB = src/arepo-$(VERSION)/libarepo.a
SYSTYPE := $(shell uname -s)

##### Modify build command as needed #####
.PHONY: $(CODELIB)
$(CODELIB): | src/arepo-$(VERSION)
	mkdir -p src/arepo-$(VERSION)/build
	cd src/arepo-$(VERSION) && /usr/bin/perl prepare-config.perl Config.sh build
	$(MAKE) -C src/arepo-$(VERSION) -j $(CPU_COUNT) SYSTYPE="$(SYSTYPE)" \
		GSL_INCL="$(GSL_FLAGS)" \
		GSL_LIB="$(GSL_LIBS)" \
		MPICH_INCL="$(shell mpicxx --showme:compile)" \
		MPICH_LIB="$(shell mpicxx --showme:link)" \
		HDF5_INCL="$(HDF5_CPPFLAGS) -DH5_USE_16_API" \
		HDF5_LIB="$(HDF5_LDFLAGS) $(HDF5_LIBS)" \
		libarepo.a


# Building the workers
arepo_worker.h: interface.py
	amusifier --type=h interface.py ArepoInterface -o $@

arepo_worker.cc: interface.py
	amusifier --type=c interface.py ArepoInterface -o $@

arepo_worker.o: arepo_worker.cc arepo_worker.h
	$(MPICXX) -c -o $@ $(CFLAGS) $<

arepo_worker: interface.o arepo_worker.o $(CODELIB)
	$(MPICXX) -o $@ $(LDFLAGS) $^ $(LDLIBS)


interface.o: interface.cc arepo_worker.h $(CODELIB)
	$(MPICXX) -o $@ -c $(CFLAGS) $<


# Which packages contain which workers?
##### Add and/or remove as needed #####
amuse-arepo_contains: arepo_worker

amuse-arepo-SUFFIX_contains: arepo_SUFFIX_worker


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


# Cleaning up
.PHONY: clean
clean:
	$(MAKE) -C src/ clean
	rm -rf *.o *.mod *worker*

.PHONY: distclean
distclean: clean
	rm -rf src/ arepo-$(VERSION).tar.gz
	rm -f support/config.mk support/config.log support/config.status
	rm -rf support/autom4te.cache
