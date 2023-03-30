Name: wrapme
Version: 0.1
Release: 1
Summary: Container wrapping RPM
License: Apache-2.0
Source0:	%{name}-%{version}.tar.gz

BuildRequires: podman

Requires: podman

%description
Wrap a container and its Quadlet file inside an RPM

%global debug_package %{nil}

%prep
%setup -c -q

%post
podman pull quay.io/yblum/wrapme:0.1

%build
podman build -t quay.io/yblum/wrapme:0.1 .

%install
podman push quay.io/yblum/wrapme:0.1
install -m 755 -d %{buildroot}%{_sysconfdir}/containers/systemd
install -m 644 wrapme.container %{buildroot}%{_sysconfdir}/containers/systemd

%files
%{_sysconfdir}/containers/systemd/wrapme.container

