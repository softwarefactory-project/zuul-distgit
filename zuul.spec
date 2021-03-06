%global commit  5c2735946ab5cd9fbe10b76cda4dbd549b79b9d7

Name:           zuul
Version:        2.5.1
Release:        22.20170920.5c273594%{?dist}
Summary:        Trunk Gating System

License:        ASL 2.0
URL:            http://docs.openstack.org/infra/system-config/
Source0:        https://github.com/openstack-infra/zuul/archive/%{commit}.tar.gz
Source1:        zuul-server.service
Source2:        zuul-merger.service
Source3:        zuul-launcher.service
Source20:       sysconfig

Patch0:         0001-Read-all-Gerrit-events-from-poll-interruption.patch
Patch1:         0001-Keep-existing-loggers-with-fileConfig.patch
Patch2:         0001-zuul-tmp-url-key.patch
Patch3:         0001-Fix-Third-Party-CI-Conflict.patch
Patch4:         0001-Find-fallback-branch-in-zuul-cloner.patch
Patch5:         0001-Don-t-getChange-on-source-not-triggering-a-change.patch
# Zuul-launcher fixup
Patch6:         0001-launcher-support-jenkins-job-builder-2.patch
Patch7:         0002-launcher-support-unicode-value-in-boolify.patch
Patch8:         0003-launcher-ensure-builder-scripts-are-removed.patch
Patch9:         0004-launcher-store-console-log-in-workspace.patch
Patch10:        0005-launcher-terminate-console-server-after-job-ends.patch
Patch12:        0006-launcher-add-simple-email-publisher.patch
Patch17:        0007-launcher-add-Jenkins-credentials-binding-support.patch
# sql-reporter fixup
Patch13:        0001-sql-reporter-add-support-for-Ref-change.patch
Patch14:        0001-sql-connection-make-_setup_tables-staticmethod.patch
Patch15:        0001-connections-only-configure-sql-on-the-server.patch
Patch16:        0001-Ensure-build.start_time-is-defined.patch
# final jenkins fix
Patch18:        0001-model-keep-jenkins-url-as-is.patch
# Gerrit 2.13 fix
Patch19:        0001-Case-sensitive-label-matching.patch
# Ansible 2.4.0 fix
Patch20:        0008-Use-inventory-instead-of-hostfile-ansible-2.4-deprec.patch
# Avoid potential offending key that can stuck the config-update
Patch21:        0009-Set-UserKnownHostsFile-to-dev-null.patch

BuildArch:      noarch

Requires:       python-pbr
Requires:       PyYAML
Requires:       python-paste
Requires:       python-webob
Requires:       python-paramiko
Requires:       GitPython
Requires:       python-ordereddict
Requires:       python-daemon
Requires:       python-extras
Requires:       python2-statsd
Requires:       python-voluptuous
Requires:       python-gear
Requires:       python2-APScheduler
Requires:       python-prettytable
Requires:       python2-babel
Requires:       python-six
Requires:       python-sqlalchemy
Requires:       python-alembic
Requires:       python2-PyMySQL
Requires:       python-crypto

BuildRequires:  python2-devel
BuildRequires:  python-pbr
BuildRequires:  python-setuptools
BuildRequires:  systemd
# Webui reqs
BuildRequires:  python2-rjsmin
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
Requires: wait4service

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
Requires: python2-jenkins-job-builder
Requires: python-zmq

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
# Add alembic __init__.py file, otherwise the migration script isn't packaged
touch zuul/alembic/__init__.py \
      zuul/alembic/sql_reporter/__init__.py \
      zuul/alembic/sql_reporter/versions/__init__.py
PBR_VERSION=%{version} %{__python2} setup.py build
mkdir build/web-assets
python2 -mrjsmin < etc/status/public_html/zuul.app.js > build/web-assets/zuul.app.min.js
python2 -mrjsmin < etc/status/public_html/jquery.zuul.js > build/web-assets/jquery.zuul.min.js
pyscss -o build/web-assets/zuul.min.css etc/status/public_html/styles/zuul.css


%install
PBR_VERSION=%{version} %{__python2} setup.py install --skip-build --root %{buildroot}
install -p -D -m 0644 %{SOURCE1} %{buildroot}%{_unitdir}/zuul-server.service
install -p -D -m 0644 %{SOURCE2} %{buildroot}%{_unitdir}/zuul-merger.service
install -p -D -m 0644 %{SOURCE3} %{buildroot}%{_unitdir}/zuul-launcher.service
install -p -D -m 0644 etc/layout.yaml-sample %{buildroot}%{_sysconfdir}/zuul/layout.yaml
install -p -D -m 0644 etc/logging.conf-sample %{buildroot}%{_sysconfdir}/zuul/logging.conf
install -p -D -m 0640 etc/zuul.conf-sample %{buildroot}%{_sysconfdir}/zuul/zuul.conf
install -p -D -m 0644 %{SOURCE20} %{buildroot}%{_sysconfdir}/sysconfig/zuul
install -p -d -m 0700 %{buildroot}%{_sharedstatedir}/zuul
install -p -d -m 0700 %{buildroot}%{_var}/log/zuul
install -p -d -m 0700 %{buildroot}%{_sharedstatedir}/zuul/jobs
install -p -d -m 0755 %{buildroot}%{_sharedstatedir}/zuul/git
install -p -d -m 0755 %{buildroot}%{_sysconfdir}/zuul/jobs

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
%systemd_post zuul-server.service
%post merger
%systemd_post zuul-merger.service
%post launcher
%systemd_post zuul-launcher.service


%preun server
%systemd_preun zuul-server.service
%preun merger
%systemd_preun zuul-merger.service
%preun launcher
%systemd_preun zuul-launcher.service


%postun server
%systemd_postun_with_restart zuul-server.service
%postun merger
%systemd_postun_with_restart zuul-merger.service
%postun launcher
%systemd_postun_with_restart zuul-launcher.service


%files
%config(noreplace) %attr(0640, root, zuul) %{_sysconfdir}/zuul/zuul.conf
%config(noreplace) %{_sysconfdir}/zuul/logging.conf
%config(noreplace) %{_sysconfdir}/zuul/layout.yaml
%config(noreplace) %{_sysconfdir}/sysconfig/zuul
%dir %{_sysconfdir}/zuul/jobs
%dir %attr(0751, zuul, zuul) %{_sharedstatedir}/zuul
%dir %attr(0750, zuul, zuul) %{_var}/log/zuul
%{python2_sitelib}/zuul
%{python2_sitelib}/zuul-*.egg-info
%{_bindir}/zuul

%files webui
/usr/share/javascript/zuul

%files server
%{_bindir}/zuul-server
%{_unitdir}/zuul-server.service

%files merger
%{_bindir}/zuul-merger
%{_unitdir}/zuul-merger.service
%dir %attr(0755, zuul, zuul) %{_sharedstatedir}/zuul/git

%files launcher
%{_bindir}/zuul-launcher
%{_unitdir}/zuul-launcher.service
%dir %attr(0700, zuul, zuul) %{_sharedstatedir}/zuul/jobs

%files cloner
%{_bindir}/zuul-cloner


%changelog
* Mon Dec 18 2017 Tristan Cacqueray <tdecacqu@redhat.com> - 2.5.1-22
- Switch requirement to python-paramiko instead of python2-paramiko

* Thu Nov 09 2017 Fabien Boucher <fboucher@redhat.com> - 2.5.1-21
- Avoid potential offending key 

* Thu Oct 26 2017 Fabien Boucher <fboucher@redhat.com> - 2.5.1-20
- Add deprecated hostfile to inventory patch

* Tue Sep 26 2017 Tristan Cacqueray <tdecacqu@redhat.com> - 2.5.1-19
- Add Case sensitive label matching patch

* Wed Sep 20 2017 Tristan Cacqueray <tdecacqu@redhat.com> - 2.5.1-18
- Bump upstream reference to include gerrit 2.13 fix

* Tue Sep 05 2017 Tristan Cacqueray <tdecacqu@redhat.com> - 2.5.1-17
- Improve server and launcher restart

* Wed Jul 19 2017 Tristan Cacqueray <tdecacqu@redhat.com> - 2.5.1-16
- Fix zuul_console starting and remove PrivateTmp from zuul-launcher

* Mon Jul 17 2017 Tristan Cacqueray <tdecacqu@redhat.com> - 2.5.1-15
- Add jenkins url fix

* Thu Jul 13 2017 Tristan Cacqueray <tdecacqu@redhat.com> - 2.5.1-14
- Fix patch order

* Fri Jun 30 2017 Tristan Cacqueray <tdecacqu@redhat.com> - 2.5.1-13
- Remove zuul results patch
- Fix the sql reporter for periodic job
- Bump version

* Tue May 23 2017 Tristan Cacqueray <tdecacqu@redhat.com> - 2.5.1-12.20170310.773651a
- Remove zuul.service

* Mon May 22 2017 Tristan Cacqueray <tdecacqu@redhat.com> - 2.5.1-11.20170310.773651a
- Add jenkins credentials binding support
- Add another sql reporter fix
- Add zuul-server systemd unit (while keeping the 'zuul' one for retro compat)

* Fri May 19 2017 Tristan Cacqueray <tdecacqu@redhat.com> - 2.5.1-10.20170310.773651a
- Add another sql connection patch

* Thu May 18 2017 Tristan Cacqueray <tdecacqu@redhat.com> - 2.5.1-9.20170310.773651a
- Add sql connection patch

* Wed May 17 2017 Tristan Cacqueray <tdecacqu@redhat.com> - 2.5.1-8.20170310.773651a
- Add alembic migration script for sql reporter
- Fix sql-reporter when used in post/periodic pipelines

* Wed May 10 2017 Tristan Cacqueray <tdecacqu@redhat.com> - 2.5.1-7.20170310.773651a
- Fix missing zuul-launcher requirements
- Add zuul-launcher patches
- Fix incorrect /etc/zuul/ file config(noreplace)

* Wed Apr 26 2017 Tristan Cacqueray <tdecacqu@redhat.com> - 2.5.1-6.20170310.773651a
- Add getChange optimization patch

* Thu Apr 20 2017 Tristan Cacqueray <tdecacqu@redhat.com> - 2.5.1-5.20170310.773651a
- Add zuul-cloner fallback patch

* Tue Apr 18 2017 Tristan Cacqueray <tdecacqu@redhat.com> - 2.5.1-4
- Use rjsmin instead of uglify

* Thu Mar 30 2017 Tristan Cacqueray - 2.5.1-3
- Depends on python-voluptuous from rdo

* Wed Mar 15 2017 Tristan Cacqueray - 2.5.1-2
- Add Fix-Third-party-CI-conflict.patch

* Tue Mar 14 2017 Tristan Cacqueray - 2.5.1-1
- Initial packaging
