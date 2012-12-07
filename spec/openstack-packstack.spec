
%global git_revno %GIT_REVNO%

Name:           openstack-packstack
Version:        2012.2.2
#Release:       1%{?dist}
Release:        0.1.dev%{git_revno}%{?dist}
Summary:        Openstack Install Utility

Group:          Applications/System
License:        ASL 2.0
URL:            https://github.com/fedora-openstack/packstack
#Source0:        https://github.com/downloads/fedora-openstack/packstack/packstack-%{version}.tar.gz
Source0:        https://github.com/downloads/fedora-openstack/packstack/packstack-%{version}dev%{git_revno}.tar.gz

BuildArch:      noarch

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
packstack can be used to deploy various parts of openstack on multiple
pre installed servers over ssh. It does this be using puppet manifests to
apply puppet labs modules (https://github.com/puppetlabs/)

%prep
#%setup -n packstack-%{version}
%setup -n packstack-%{version}dev%{git_revno}

# Sanitizing a lot of the files in the puppet modules, they come from seperate upstream projects
find packstack/puppet/modules \( -name .fixtures.yml -o -name .gemfile -o -name ".travis.yml" -o -name .rspec \) -exec rm {} \;
find packstack/puppet/modules \( -name "*.py" -o -name "*.rb" -o -name "*.pl" \) -exec sed -i '/^#!/{d;q}' {} \; -exec chmod -x {} \;
find packstack/puppet/modules \( -name "*.sh" \) -exec sed -i 's/^#!.*/#!\/bin\/bash/g' {} \; -exec chmod +x {} \;
find packstack/puppet/modules -name site.pp -size 0 -exec rm {} \;

# Moving this data directory out temporarily as it causes setup.py to throw errors
rm -rf %{_builddir}/puppet
mv packstack/puppet %{_builddir}/puppet

%build
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
%doc LICENSE
%{_bindir}/packstack
%{python_sitelib}/packstack
%{python_sitelib}/packstack-%{version}*.egg-info
%{_mandir}/man1/packstack.1.gz

%changelog

* Thu Dec 06 2012 Derek Higgins <derekh@redhat.com>
- Not keeping change log here, see downstream distributions for actual packaging

