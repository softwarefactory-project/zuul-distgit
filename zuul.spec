%global commit  773651ad7bf0fc6adba2357173ffb657d874478a

Name:           zuul
Version:        2.5.1
Release:        2%{?dist}
Summary:        Trunk Gating System

License:        ASL 2.0
URL:            http://docs.openstack.org/infra/system-config/
Source0:        https://github.com/openstack-infra/zuul/archive/%{commit}.tar.gz
Source1:        zuul.service
Source2:        zuul-merger.service
Source3:        zuul-launcher.service
Source20:       sysconfig

Patch0:         0001-Read-all-Gerrit-events-from-poll-interruption.patch
Patch1:         0001-Keep-existing-loggers-with-fileConfig.patch
Patch2:         0001-zuul-tmp-url-key.patch
Patch3:         Fix-Third-party-CI-conflict.patch

BuildArch:      noarch

Requires:       python-pbr
Requires:       PyYAML
Requires:       python-paste
Requires:       python-webob
Requires:       python2-paramiko
Requires:       GitPython
Requires:       python-ordereddict
Requires:       python-daemon
Requires:       python-extras
Requires:       python2-statsd
Requires:       python2-voluptuous
Requires:       python-gear
Requires:       python2-APScheduler
Requires:       python-prettytable
Requires:       python2-babel
Requires:       python-six
Requires:       python-sqlalchemy
Requires:       python-alembic

BuildRequires:  python2-devel
BuildRequires:  python-pbr
BuildRequires:  python-setuptools
BuildRequires:  systemd
# Webui reqs
BuildRequires:  uglify-js
BuildRequires:  python-pathlib
BuildRequires:  python-enum34
BuildRequires:  python-scss


%description
Zuul is a project gating system developed for the OpenStack Project.


%package webui
Summary: The Zuul web interface

%description webui
The Zuul web interface


%package server
Summary: The Zuul server
Requires: zuul

%description server
The Zuul server


%package merger
Summary: The Zuul merger
Requires: zuul

%description merger
The Zuul merger


%package launcher
Summary: The Zuul launcher
Requires: zuul

%description launcher
The Zuul launcher


%package cloner
Summary: The Zuul cloner
Requires: zuul

%description cloner
The Zuul cloner


%prep
%autosetup -n %{name}-%{commit} -p1
rm requirements.txt test-requirements.txt


%build
PBR_VERSION=%{version} %{__python2} setup.py build
mkdir build/web-assets
uglifyjs -o build/web-assets/zuul.app.min.js etc/status/public_html/zuul.app.js
uglifyjs -o build/web-assets/jquery.zuul.min.js etc/status/public_html/jquery.zuul.js
pyscss -o build/web-assets/zuul.min.css etc/status/public_html/styles/zuul.css


%install
PBR_VERSION=%{version} %{__python2} setup.py install --skip-build --root %{buildroot}
install -p -D -m 0644 %{SOURCE1} %{buildroot}%{_unitdir}/zuul.service
install -p -D -m 0644 %{SOURCE2} %{buildroot}%{_unitdir}/zuul-merger.service
install -p -D -m 0644 %{SOURCE3} %{buildroot}%{_unitdir}/zuul-launcher.service
install -p -D -m 0644 etc/layout.yaml-sample %{buildroot}%{_sysconfdir}/zuul/layout.yaml
install -p -D -m 0644 etc/logging.conf-sample %{buildroot}%{_sysconfdir}/zuul/logging.conf
install -p -D -m 0640 etc/zuul.conf-sample %{buildroot}%{_sysconfdir}/zuul/zuul.conf
install -p -D -m 0644 %{SOURCE20} %{buildroot}%{_sysconfdir}/sysconfig/zuul
install -p -d -m 0700 %{buildroot}%{_sharedstatedir}/zuul
install -p -d -m 0700 %{buildroot}%{_var}/log/zuul

install -p -D -m 0644 build/web-assets/zuul.app.min.js %{buildroot}/usr/share/javascript/zuul/js/zuul.app.min.js
install -p -D -m 0644 build/web-assets/jquery.zuul.min.js %{buildroot}/usr/share/javascript/zuul/js/jquery.zuul.min.js
install -p -D -m 0644 build/web-assets/zuul.min.css %{buildroot}/usr/share/javascript/zuul/css/zuul.min.css
for image in etc/status/public_html/images/*.png; do
    install -p -D -m 0644 ${image} %{buildroot}/usr/share/javascript/zuul/images/$(basename ${image})
done


%pre
getent group zuul >/dev/null || groupadd -r zuul
if ! getent passwd zuul >/dev/null; then
  useradd -r -g zuul -G zuul -d %{_sharedstatedir}/zuul -s /sbin/nologin -c "Zuul Daemon" zuul
fi
exit 0


%post server
%systemd_post zuul.service
%post merger
%systemd_post zuul-merger.service
%post launcher
%systemd_post zuul-launcher.service


%preun server
%systemd_preun zuul.service
%preun merger
%systemd_preun zuul-merger.service
%preun launcher
%systemd_preun zuul-launcher.service


%postun server
%systemd_postun_with_restart zuul.service
%postun merger
%systemd_postun_with_restart zuul-merger.service
%postun launcher
%systemd_postun_with_restart zuul-launcher.service


%files
%{_sysconfdir}/zuul/*
%config(noreplace) %attr(0644, root, root) %{_sysconfdir}/zuul/layout.yaml
%config(noreplace) %attr(0640, root, zuul) %{_sysconfdir}/zuul/zuul.conf
%config(noreplace) %{_sysconfdir}/sysconfig/zuul
%dir %attr(0750, zuul, zuul) %{_sharedstatedir}/zuul
%dir %attr(0750, zuul, zuul) %{_var}/log/zuul
%{python2_sitelib}/zuul
%{python2_sitelib}/zuul-*.egg-info
%{_bindir}/zuul

%files webui
/usr/share/javascript/zuul

%files server
%{_bindir}/zuul-server
%{_unitdir}/zuul.service

%files merger
%{_bindir}/zuul-merger
%{_unitdir}/zuul-merger.service

%files launcher
%{_bindir}/zuul-launcher
%{_unitdir}/zuul-launcher.service

%files cloner
%{_bindir}/zuul-cloner


%changelog
* Wed Mar 15 2017 Tristan Cacqueray - 2.5.1-2
- Add Fix-Third-party-CI-conflict.patch

* Tue Mar 14 2017 Tristan Cacqueray - 2.5.1-1
- Initial packaging
