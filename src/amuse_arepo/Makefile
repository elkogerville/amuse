ifneq (,$(filter-out clean distclean, $(MAKECMDGOALS)))
include support/config.mk
endif


# Detecting dependencies
support/config.mk:
	cd support && ./configure


# Downloading the code
VERSION = c2383a9f2b57349561775a2b67de6044cd389580
arepo-$(VERSION).tar.gz:
	$(DOWNLOAD) https://github.com/elkogerville/Arepo/archive/$(VERSION).tar.gz >$@


src/arepo-$(VERSION): arepo-$(VERSION).tar.gz
	tar xf $<
	mkdir -p src/
	mv arepo-$(VERSION) src/
	cp configs/galaxy_merger_config.sh src/arepo-$(VERSION)/Config.sh
# cp src/arepo-$(VERSION)/Template-Config.sh src/arepo-$(VERSION)/Config.sh


# Building the code into a static library
##### Remove anything not needed #####
# DEPFLAGS += $(STOPCOND_CFLAGS) $(STOPCONDMPI_CFLAGS) $(AMUSE_MPI_CFLAGS)
# DEPFLAGS += $(SIMPLE_HASH_CFLAGS) $(G6LIB_CFLAGS)
# DEPFLAGS += $(SAPPORO_LIGHT_CFLAGS)

##### Pick whichever language is applicable for the code #####
# DEPFLAGS += $(OPENMP_CFLAGS) $(OPENMP_FFLAGS) $(OPENMP_CXXFLAGS)


DEPFLAGS += $(GSL_FLAGS)
DEPFLAGS += $(GMP_FLAGS)
DEPFLAGS += $(FFTW_FLAGS)
DEPFLAGS += $(HDF5_CFLAGS)

CFLAGS += $(DEPFLAGS)
CFLAGS += -I src/arepo-$(VERSION)/src
CFLAGS += -I src/arepo-$(VERSION)/build


# LDLIBS += -lm $(STOPCOND_LIBS) $(STOPCONDMPI_LIBS) $(AMUSE_MPI_LIBS)

LDLIBS += $(GSL_LIBS)
LDLIBS += $(GMP_LIBS)
LDLIBS += $(FFTW_LIBS)
LDLIBS += $(HDF5_LIBS) $(HDF5_FLIBS)
LDLIBS += $(shell mpicxx --showme:link)

CODELIB = src/arepo-$(VERSION)/libarepo.a
SYSTYPE := $(shell uname -s)
MPI_COMPILE_FLAGS := $(shell mpicxx --showme:compile)
MPI_LINK_FLAGS := $(shell mpicxx --showme:link)


.PHONY: $(CODELIB)
$(CODELIB): | src/arepo-$(VERSION)
	mkdir -p src/arepo-$(VERSION)/build
	cd src/arepo-$(VERSION) && /usr/bin/perl prepare-config.perl Config.sh build
	$(MAKE) -C src/arepo-$(VERSION) -j 1 SYSTYPE="$(SYSTYPE)" \
		GSL_INCL="$(GSL_FLAGS)" \
		GSL_LIB="$(GSL_LIBS)" \
		MPICH_INCL="$(MPI_COMPILE_FLAGS)" \
		MPICH_LIB="$(MPI_LINK_FLAGS)" \
		HDF5_INCL="$(HDF5_CPPFLAGS) -DH5_USE_16_API" \
		HDF5_LIB="$(HDF5_LDFLAGS) $(HDF5_LIBS)" \
		build/main/main.o libarepo.a


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
amuse-arepo_contains: arepo_worker

# amuse-arepo-SUFFIX_contains: arepo_SUFFIX_worker


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
	rm -rf *.o *.mod *worker*

.PHONY: distclean
distclean: clean
	rm -f support/config.mk support/config.log support/config.status
	rm -rf support/autom4te.cache
