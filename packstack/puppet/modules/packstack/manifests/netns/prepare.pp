
class packstack::netns::prepare (
    $rdo_rpm_url = 'http://repos.fedorapeople.org/repos/openstack/openstack-grizzly/rdo-release-grizzly-3.noarch'
){
    exec { "rdo_repo_install":
        path => "/usr/bin/",
        command => "yum localinstall -y $rdo_rpm_url",
    }
}
