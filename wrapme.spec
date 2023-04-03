Name: wrapme
Version: 0.1
Release: 1
Summary: Container wrapping RPM
License: Apache-2.0
Source0:	%{name}-%{commit}.tar.gz

%global debug_package %{nil}

%global image quay.io/yblum/wrapme:%{version}-%{release}

%description
Generic description

%prep
%setup -c -q

%install
install -m 755 -d %{buildroot}%{_sysconfdir}/containers/systemd
install -m 644 mysql/wrapme-mysql.* %{buildroot}%{_sysconfdir}/containers/systemd
install -m 644 network/* %{buildroot}%{_sysconfdir}/containers/systemd
install -m 755 -d %{buildroot}%{_libexecdir}
install -m 755 mysql/wrapme-mysql-secrets.sh %{buildroot}%{_libexecdir}

%files

%package network
Summary: Podman network for wrapme
Requires: podman

%description network
Quadlet Network file for wrapme

%files network
%{_sysconfdir}/containers/systemd/wrapme.network

%package mysql-secrets
Summary: Secrets for MySQL Server
Requires: podman

%description mysql-secrets
The MySQL service require storing its password as both raw and kubernetes based podman secrets

%post mysql-secrets
%{_libexecdir}/wrapme-mysql-secrets.sh create

%preun mysql-secrets
%{_libexecdir}/wrapme-mysql-secrets.sh remove

%files mysql-secrets
%{_libexecdir}/wrapme-mysql-secrets.sh

%package mysql
Summary: MySQL service
Requires: podman
BuildRequires: podman
Requires: %{name}-network = %{version}-%{release}
Requires: %{name}-mysql-secrets = %{version}-%{release}

%description mysql
The MySQL service for the wrapme package

%global mysql_image docker.io/library/mysql:5.6

%pre mysql
podman pull %{mysql_image}

%postun mysql
podman image rm %{mysql_image}

%files mysql
%{_sysconfdir}/containers/systemd/wrapme-mysql.container
%{_sysconfdir}/containers/systemd/wrapme-mysql.volume
