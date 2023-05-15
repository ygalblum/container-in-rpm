COMMIT = $(shell (cd "$(SRCDIR)" && git rev-parse HEAD))

RPM_SPECFILE=rpmbuild/SPECS/container-in-rpm.spec
RPM_TARBALL=rpmbuild/SOURCES/container-in-rpm-$(COMMIT).tar.gz

$(RPM_SPECFILE): container-in-rpm.spec
	mkdir -p $(CURDIR)/rpmbuild/SPECS
	cp container-in-rpm.spec $(RPM_SPECFILE)

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

