Name: {{{ git_dir_name }}}
Version: {{{ git_dir_version }}}
Release: 1%{?dist}
Summary: Container wrapping RPM

License: Apache-2.0
URL: https://github.com/ygalblum/container-in-rpm
VCS: {{{ git_dir_vcs }}}

Source:	{{{ git_dir_pack }}}

%global debug_package %{nil}

%description
Generic description

%prep
{{{ git_dir_setup_macro }}}

%changelog
{{{ git_dir_changelog }}}

%install
install -m 755 -d %{buildroot}%{_sysconfdir}/containers/systemd
install -m 644 mysql/container-in-rpm-mysql.* %{buildroot}%{_sysconfdir}/containers/systemd
install -m 644 network/* %{buildroot}%{_sysconfdir}/containers/systemd
install -m 755 -d %{buildroot}/opt/container-in-rpm
install -m 755 mysql/container-in-rpm-mysql-secrets.sh %{buildroot}/opt/container-in-rpm
install -m 755 app/container-in-rpm-app-secret.sh %{buildroot}/opt/container-in-rpm
install -m 644 app/container-in-rpm-csr-config.cnf %{buildroot}/opt/container-in-rpm
install -m 644 app/container-in-rpm-app.* %{buildroot}%{_sysconfdir}/containers/systemd
install -m 644 app/envoy-proxy-configmap.yml %{buildroot}%{_sysconfdir}/containers/systemd

%files

%package network
Summary: Podman network for container-in-rpm
Requires: podman

%description network
Quadlet Network file for container-in-rpm

%files network
%{_sysconfdir}/containers/systemd/container-in-rpm.network

%package mysql-secrets
Summary: Secrets for MySQL Server
Requires: podman

%description mysql-secrets
The MySQL service require storing its password as both raw and kubernetes based podman secrets

%post mysql-secrets
/opt/container-in-rpm/container-in-rpm-mysql-secrets.sh create

%preun mysql-secrets
if [ $1 -eq 0 ]; then
    /opt/container-in-rpm/container-in-rpm-mysql-secrets.sh remove
fi

%files mysql-secrets
/opt/container-in-rpm/container-in-rpm-mysql-secrets.sh

%package mysql
Summary: MySQL service
Requires: podman
Requires: %{name}-network = %{version}-%{release}
Requires: %{name}-mysql-secrets = %{version}-%{release}

%description mysql
The MySQL service for the container-in-rpm package

%global mysql_image docker.io/library/mysql:5.6

%pre mysql
/usr/bin/podman pull %{mysql_image}

%postun mysql
if [ $1 -eq 0 ]; then
    /usr/bin/podman image rm %{mysql_image}
fi

%files mysql
%{_sysconfdir}/containers/systemd/container-in-rpm-mysql.container
%{_sysconfdir}/containers/systemd/container-in-rpm-mysql.volume

%package app-secrets
Summary: Secrets for Envoy Proxy Server
Requires: podman
Requires: openssl

%description app-secrets
The Envoy Proxy service requires a self signed certificate

%post app-secrets
/opt/container-in-rpm/container-in-rpm-app-secret.sh create

%preun app-secrets
if [ $1 -eq 0 ]; then
    /opt/container-in-rpm/container-in-rpm-app-secret.sh remove
fi

%files app-secrets
/opt/container-in-rpm/container-in-rpm-app-secret.sh
/opt/container-in-rpm/container-in-rpm-csr-config.cnf

%package app
Summary: Wordpress service with Envoy proxy
Requires: podman
Requires: %{name}-network = %{version}-%{release}
Requires: %{name}-mysql = %{version}-%{release}
Requires: %{name}-app-secrets = %{version}-%{release}

%description app
The Wordpress service wrapped with Envoy proxy for the container-in-rpm package

%global wordpress_image docker.io/library/wordpress:4.9-apache
%global envoy_image docker.io/envoyproxy/envoy:v1.25.0

%pre app
/usr/bin/podman pull %{wordpress_image}
/usr/bin/podman pull %{envoy_image}

%postun app
if [ $1 -eq 0 ]; then
    /usr/bin/podman image rm %{wordpress_image}
    /usr/bin/podman image rm %{envoy_image}
fi

%files app
%{_sysconfdir}/containers/systemd/container-in-rpm-app.kube
%{_sysconfdir}/containers/systemd/container-in-rpm-app.yml
%{_sysconfdir}/containers/systemd/envoy-proxy-configmap.yml
