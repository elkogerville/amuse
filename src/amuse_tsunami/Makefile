ifneq (,$(filter-out clean distclean, $(MAKECMDGOALS)))
include support/config.mk
endif

# Detecting dependencies
support/config.mk:
	cd support && ./configure

tsunami.tar.gz:
	@echo "Add message here"

# PATCHES := $(shell cat patches/series)

src/tsunami-master: | tsunami.tar.gz
	##### Modify as needed #####
	tar xf $<
	mv tsunami-master src/
	# ##### Apply patches here, if needed #####
	# patch <patch.patch
	# for p in $(PATCHES) ; do patch -p1 <patches/$$p ; done


# Building the code into a static library
DEPFLAGS += $(STOPCOND_CFLAGS)

# ##### Pick whichever language is applicable for the code #####
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
# LDFLAGS += $(CUDA_LDFLAGS)

LDLIBS += -lm $(STOPCOND_LIBS)
# LDLIBS += $(SIMPLE_HASH_LIBS) $(G6LIB_LIBS)
# LDLIBS += $(SAPPORO_LIGHT_LIBS)

# TODO CUDA, anything else?
# LDLIBS += $(CL_LIBS)
# LDLIBS += $(LAPACK_LIBS) $(BLAS_LIBS) $(LIBS) $(FLIBS)
# LDLIBS += $(GSL_LIBS)
# LDLIBS += $(GMP_LIBS)
# LDLIBS += $(MPFR_LIBS)
# LDLIBS += $(FFTW_LIBS)
##### Pick whichever language is applicable for the code #####
# LDLIBS += $(HDF5_LIBS) $(HDF5_FLIBS)
# ##### Pick whichever language is applicable for the code #####
# LDLIBS += $(NETCDF4_LIBS) $(NETCDF4_FLIBS)

CODELIB = src/tsunami-master/build/lib/libtsunamicore.a

##### Modify build command as needed #####
.PHONY: $(CODELIB)
$(CODELIB): | src/tsunami-master
	cd src/tsunami-master/build && cmake .. -Dcpp=on -DCMAKE_OSX_ARCHITECTURES=arm64
	$(MAKE) -C src/tsunami-master/build -j $(CPU_COUNT)

# Building the workers
tsunami_worker.h: interface.py
	amusifier --type=h interface.py TsunamiInterface -o $@

tsunami_worker.cc: interface.py
	amusifier --type=c interface.py TsunamiInterface -o $@

tsunami_worker.o: tsunami_worker.cc tsunami_worker.h
	$(MPICXX) -c -o $@ $(CFLAGS) $<

# tsunami_worker: interface.o tsunami_worker.o $(CODELIB)
# 	$(MPICXX) -o $@ $(LDFLAGS) $^ $(LDLIBS)

tsunami_worker: $(CODELIB)

interface.o: interface.cc tsunami_worker.h
	$(MPICXX) -o $@ -c $(CFLAGS) $<


# Which packages contain which workers?
##### Add and/or remove as needed #####
amuse-tsunami_contains: tsunami_worker

amuse-tsunami-SUFFIX_contains: tsunami_SUFFIX_worker


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
	rm -rf src/tsunami-master/build/*
	rm -rf *.o *.mod *worker*

.PHONY: distclean
distclean: clean
	rm -f support/config.mk support/config.log support/config.status
	rm -rf support/autom4te.cache
