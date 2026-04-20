ifneq (,$(filter-out clean distclean, $(MAKECMDGOALS)))
include support/config.mk
endif

# Detecting dependencies
support/config.mk:
	cd support && ./configure

tsunami.tar.gz:
	@echo "Add message here"


src/tsunami-master: | tsunami.tar.gz
	# tar xf $<
	tar xf tsunami.tar.gz # FIXME
	mv tsunami-master src/

# NOTE: how do stopconds work when in python only mode?

.PHONY: install_tsunami
install_tsunami: | src/tsunami-master
ifneq ($(CONDA_PREFIX),)
	conda install --yes --channel conda-forge --override-channels numpy swig scikit-build-core
endif
	cd src/tsunami-master/build && cmake .. -DCMAKE_OSX_ARCHITECTURES=arm64 # FIXME: maybe we should ensure that build is clean and exists
	$(MAKE) -C src/tsunami-master/build -j $(CPU_COUNT)

# Building the workers
# tsunami_worker.h: interface.py
# 	amusifier --type=h interface.py TsunamiInterface -o $@

# tsunami_worker.cc: interface.py
# 	amusifier --type=c interface.py TsunamiInterface -o $@

# tsunami_worker.o: tsunami_worker.cc tsunami_worker.h
# 	$(MPICXX) -c -o $@ $(CFLAGS) $<

# tsunami_worker: interface.o tsunami_worker.o $(CODELIB)
# 	$(MPICXX) -o $@ $(LDFLAGS) $^ $(LDLIBS)

tsunami_worker: interface.py
	PYTHONPATH=. amusifier --type=py --mode=mpi -x interface TsunamiInterface TsunamiImplementation -o $@

# Which packages contain which workers?
amuse-tsunami_contains: tsunami_worker


# Building and installing packages
develop-%: %_contains install_tsunami # FIXME
	support/shared/uninstall.sh $*
	python -m pip install -e packages/$*

install-%: %_contains install_tsunami
	support/shared/uninstall.sh $*
	python -m pip install packages/$*

package-%: %_contains
	python3 -m pip install -vv --no-cache-dir --no-deps --no-build-isolation --prefix ${PREFIX} packages/$*

test-%:
	cd packages/$* && pytest


# Cleaning up
.PHONY: clean
clean:
	rm -rf *worker*

.PHONY: distclean
distclean: clean
	rm -f support/config.mk support/config.log support/config.status
	rm -rf support/autom4te.cache
