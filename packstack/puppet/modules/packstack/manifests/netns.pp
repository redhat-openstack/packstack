#
# Checks if netns is supported and if not updates kernel, iputils
# and iproute

class packstack::netns (
    $rdo_repo_url = 'http://repos.fedorapeople.org/repos/openstack/openstack-grizzly/',
    $rdo_rpm_nvr = 'rdo-release-grizzly-3.noarch',
    $warning = "Kernel package with netns support has been installed."
)
{
    if $::netns_support != "true" {
        exec { "netns_dependecy_install":
            path => "/usr/bin/",
            command => "yum update -y kernel iputils iproute"
        }

        if $::has_rdo != "true" {
            stage { 'prepare':
                before => Stage['main'],
            }
            stage { 'cleanup':
                require => Stage['main'],
            }

            class {'packstack::netns::prepare':
                rdo_rpm_url => "${rdo_repo_url}${rdo_rpm_nvr}.rpm",
                stage => prepare,
            }

            class {'packstack::netns::cleanup':
                rdo_rpm_nvr => $rdo_rpm_nvr,
                stage => cleanup,
            }
        }

        notify { "packstack_info":
            message => $warning,
            require => Exec["netns_dependecy_install"],
        }
    }
}
