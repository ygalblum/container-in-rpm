COMMIT = $(shell (cd "$(SRCDIR)" && git rev-parse HEAD))

container-build:
	podman build -t quay.io/yblum/wrapme:0.1 .

container-push:
	podman push quay.io/yblum/wrapme:0.1

container-install:
	podman pull quay.io/yblum/wrapme:0.1

RPM_SPECFILE=rpmbuild/SPECS/wrapme.spec
RPM_TARBALL=rpmbuild/SOURCES/wrapme-$(COMMIT).tar.gz

$(RPM_SPECFILE): wrapme.spec
	mkdir -p $(CURDIR)/rpmbuild/SPECS
	cp wrapme.spec $(RPM_SPECFILE)

$(RPM_TARBALL):
	mkdir -p $(CURDIR)/rpmbuild/SOURCES
	git archive --format=tar.gz HEAD > $(RPM_TARBALL)

.PHONY: srpm
srpm: $(RPM_SPECFILE) $(RPM_TARBALL)
	rpmbuild -bs \
		--define "_topdir $(CURDIR)/rpmbuild" \
		--define "commit $(COMMIT)" \
		--with tests \
		$(RPM_SPECFILE)

.PHONY: rpm
rpm: $(RPM_SPECFILE) $(RPM_TARBALL)
	rpmbuild -bb \
		--define "_topdir $(CURDIR)/rpmbuild" \
		--define "commit $(COMMIT)" \
		--with tests \
		$(RPM_SPECFILE)

.PHONY: scratch
scratch: $(RPM_SPECFILE) $(RPM_TARBALL)
	rpmbuild -bb \
		--define "_topdir $(CURDIR)/rpmbuild" \
		--define "commit $(COMMIT)" \
		--without tests \
		--nocheck \
		$(RPM_SPECFILE)

