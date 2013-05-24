
class packstack::netns::cleanup (
    $rdo_rpm_nvr = 'rdo-release-grizzly-3.noarch'
) {
    exec { "rdo_repo_uninstall":
        path => "/usr/bin/",
        command => "yum remove -y $rdo_rpm_nvr",
    }
}
