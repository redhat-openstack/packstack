
%global git_revno %GIT_REVNO%

Name:           openstack-packstack
Version:        2012.2.1
#Release:       1%{?dist}
Release:        1dev%{git_revno}%{?dist}
Summary:        Openstack Install Utility

License:        ASL 2.0
URL:            https://github.com/fedora-openstack/packstack
#Source0:        https://github.com/downloads/fedora-openstack/packstack/packstack-%{version}.tar.gz
Source0:        https://github.com/downloads/fedora-openstack/packstack/packstack-%{version}dev%{git_revno}.tar.gz

BuildArch:      noarch

BuildRequires:  make
BuildRequires:  python2-devel
BuildRequires:  python-setuptools
%if 0%{?rhel}
BuildRequires:  python-sphinx10
%else
BuildRequires:  python-sphinx
%endif

Requires:       openssh-clients

%description
Packstack is a utility that uses puppet modules to install openstack
packstack can be used to deploy variouse parts of openstack on multiple
pre installed servers over ssh. It does this be using puppet manifests to 
apply puppetlabs modules (https://github.com/puppetlabs/)

%prep
#%setup -n packstack-%{version}
%setup -n packstack-%{version}dev%{git_revno}

%build

# Moving this data directory out temporarily as it causes setup.py to throw errors
mv packstack/puppet %{_builddir}/puppet

# puppet on fedora already has this module, using this one causes problems
%if 0%{?fedora}
    rm -rf %{_builddir}/puppet/modules/create_resources
%endif

%{__python} setup.py build

cd docs
%if 0%{?rhel}
make man SPHINXBUILD=sphinx-1.0-build
%else
make man
%endif

%install
%{__python} setup.py install --skip-build --root %{buildroot}
mv %{_builddir}/puppet %{buildroot}/%{python_sitelib}/packstack/puppet

mkdir -p %{buildroot}%{_mandir}/man1
install -p -D -m 644 docs/_build/man/*.1 %{buildroot}%{_mandir}/man1/

%files
%{_bindir}/packstack
%{python_sitelib}/packstack
%{python_sitelib}/packstack-%{version}*.egg-info
%{_mandir}/man1/packstack.1.gz

%changelog

* Wed Nov 28 2012 Derek Higgins <derekh@redhat.com> - 2012.2.1-1dev186
- example packaging for Fedora / Redhat

