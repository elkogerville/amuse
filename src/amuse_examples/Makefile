# Building and installing packages
develop-%:
	support/shared/uninstall.sh $*
	python -m pip install -e packages/$*

install-%:
	support/shared/uninstall.sh $*
	python -m pip install packages/$*

package-%:
	python3 -m pip install -vv --no-cache-dir --no-deps --no-build-isolation --prefix ${PREFIX} packages/$*

test-%:
	cd packages/$* && pytest


# Cleaning up
.PHONY: clean
clean:

.PHONY: distclean
distclean: clean
