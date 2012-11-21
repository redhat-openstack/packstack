
Name:           openstack-packstack
Version:        2012.2.1
Release:        1
Summary:        Openstack Install Utility

License:        ASL 2.0
URL:            https://github.com/fedora-openstack/packstack
Source0:        https://github.com/derekhiggins/packstack/archive/packstack-2012.2.1.tar.gz
Source1:        https://github.com/derekhiggins/installer/archive/installer-0.1.tar.gz 

Source10:       https://github.com/puppetlabs/openstack_0.0.tmp.tgz
Source11:       https://github.com/puppetlabs/keystone_0.0.tmp.tgz
Source12:       https://github.com/puppetlabs/glance_0.0.tmp.tgz
Source13:       https://github.com/puppetlabs/nova_0.0.tmp.tgz
Source14:       https://github.com/puppetlabs/swift_0.0.tmp.tgz
Source15:       https://github.com/puppetlabs/horizon_0.0.tmp.tgz
Source16:       https://github.com/puppetlabs/cinder_0.0.tmp.tgz

Source17:       https://github.com/puppetlabs/stdlib_0.0.tmp.tgz
Source18:       https://github.com/puppetlabs/sysctl_0.0.tmp.tgz
Source19:       https://github.com/puppetlabs/mysql_0.0.tmp.tgz
Source20:       https://github.com/puppetlabs/concat_0.0.tmp.tgz
Source21:       https://github.com/puppetlabs/create_resources_0.0.tmp.tgz
Source22:       https://github.com/puppetlabs/rsync_0.0.tmp.tgz
Source23:       https://github.com/puppetlabs/xinetd_0.0.tmp.tgz
Source24:       https://github.com/puppetlabs/apache_0.0.tmp.tgz

Source25:       https://github.com/lstanden/firewall_0.0.tmp.tgz
Source26:       https://github.com/saz/memcached_0.0.tmp.tgz
Source27:       https://github.com/saz/ssh_0.0.tmp.tgz
Source28:       https://github.com/cprice-puppet/inifile_0.0.tmp.tgz
Source29:       https://github.com/derekhiggins/qpid_0.0.tmp.tgz
Source30:       https://github.com/derekhiggins/vlan_0.0.tmp.tgz

Source50:       packstack


Patch0001:      0001-config.patch
Patch0002:      0002-not-using-epel.patch

BuildArch:      noarch

BuildRequires:  python2

Requires:       python
Requires:       openssh-clients

%description
Packstack is a utility that uses puppet modules to install openstack
packstack can be used to deploy variouse parts of openstack on multiple
pre installed servers over ssh. It does this be using puppet manifests to 
apply puppetlabs modules (https://github.com/puppetlabs/)

%prep
%setup -n packstack-packstack-2012.2.1
%patch0002 -p1

%setup -T -b 1 -n installer-installer-0.1
%patch0001 -p1

%setup -T -b 10 -n openstack
%setup -T -b 11 -n keystone
%setup -T -b 12 -n glance
%setup -T -b 13 -n nova
%setup -T -b 14 -n swift
%setup -T -b 15 -n horizon
%setup -T -b 16 -n cinder
%setup -T -b 17 -n stdlib
%setup -T -b 18 -n sysctl
%setup -T -b 19 -n mysql
%setup -T -b 20 -n concat
%setup -T -b 21 -n create_resources
%setup -T -b 22 -n rsync
%setup -T -b 23 -n xinetd
%setup -T -b 24 -n apache
%setup -T -b 25 -n firewall
%setup -T -b 26 -n memcached
%setup -T -b 27 -n ssh
%setup -T -b 28 -n inifile
%setup -T -b 29 -n qpid
%setup -T -b 30 -n vlan

%build


%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_datadir} 

cp -r %{_builddir}/installer-installer-0.1 %{buildroot}%{_datadir}/installer
cp -r %{_builddir}/packstack-packstack-2012.2.1 %{buildroot}%{_datadir}/installer/packstack

find %{buildroot}%{_datadir}/installer -name "*.py" -exec python -c "import py_compile; py_compile.compile('{}')" \;

mkdir -p %{buildroot}%{_datadir}/installer/packstack/puppet/modules
for module in openstack keystone glance nova swift horizon cinder stdlib sysctl mysql concat \
              create_resources rsync xinetd apache firewall memcached ssh inifile qpid vlan; do
    cp -r %{_builddir}/$module %{buildroot}%{_datadir}/installer/packstack/puppet/modules
done

install -p -D %{SOURCE50} %{buildroot}%{_bindir}/packstack

mkdir -p %{buildroot}%{_sharedstatedir}/packstack/manifests
ln -s %{_sharedstatedir}/packstack/manifests %{buildroot}%{_datadir}/installer/packstack/puppet/manifests 

%files
%{_datadir}/installer
%{_bindir}/packstack
%{_sharedstatedir}/packstack

%changelog

* Wed Nov 14 2012 Derek Higgins <derekh@redhat.com> - 2012.2.1-1
- initial packaging

