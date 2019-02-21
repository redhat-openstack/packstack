# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import yaml

from OpenSSL import crypto
from time import time
from packstack.installer import basedefs
from packstack.installer import utils
from packstack.installer.setup_controller import Controller

controller = Controller()

PUPPET_DIR = os.path.join(basedefs.DIR_PROJECT_DIR, "puppet")
PUPPET_TEMPLATE_DIR = os.path.join(PUPPET_DIR, "templates")
HIERA_COMMON_YAML = os.path.join(basedefs.HIERADATA_DIR, "common.yaml")
# For compatibility with hiera < 3.0
HIERA_DEFAULTS_YAML = os.path.join(basedefs.HIERADATA_DIR, "defaults.yaml")


class ManifestFiles(object):
    def __init__(self):
        self.filelist = []
        self.data = {}

    # continuous manifest file that have the same marker can be
    # installed in parallel, if on different servers
    def addFile(self, filename, marker, data=''):
        self.data[filename] = self.data.get(filename, '') + '\n' + data
        for f, p in self.filelist:
            if f == filename:
                return

        self.filelist.append((filename, marker))

    def prependFile(self, filename, marker, data=''):
        self.data[filename] = data + '\n' + self.data.get(filename, '')
        for f, p in self.filelist:
            if f == filename:
                return

        self.filelist.append((filename, marker))

    def getFiles(self):
        return [f for f in self.filelist]

    def writeManifests(self):
        """
        Write out the manifest data to disk, this should only be called once
        write before the puppet manifests are copied to the various servers
        """
        os.mkdir(basedefs.PUPPET_MANIFEST_DIR, 0o700)
        for fname, data in self.data.items():
            path = os.path.join(basedefs.PUPPET_MANIFEST_DIR, fname)
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, 'w') as fp:
                fp.write(data)
manifestfiles = ManifestFiles()


def getManifestTemplate(template_name):
    if not template_name.endswith(".pp"):
        template_name += ".pp"
    with open(os.path.join(PUPPET_TEMPLATE_DIR, template_name)) as fp:
        return fp.read() % controller.CONF


def appendManifestFile(manifest_name, data, marker=''):
    manifestfiles.addFile(manifest_name, marker, data)


def generateHieraDataFile():
    os.mkdir(basedefs.HIERADATA_DIR, 0o700)
    with open(HIERA_COMMON_YAML, 'w') as outfile:
        outfile.write(yaml.dump(controller.CONF,
                                explicit_start=True,
                                default_flow_style=False))
    os.symlink(os.path.basename(HIERA_COMMON_YAML), HIERA_DEFAULTS_YAML)


def generate_ssl_cert(config, host, service, ssl_key_file, ssl_cert_file):
    """
    Wrapper on top of openssl
    """
    # We have to check whether the certificate already exists
    cert_dir = os.path.join(config['CONFIG_SSL_CERT_DIR'], 'certs')
    local_cert_name = host + os.path.basename(ssl_cert_file)
    local_cert_path = os.path.join(cert_dir, local_cert_name)
    if not os.path.exists(local_cert_path):
        ca_file = open(config['CONFIG_SSL_CACERT_FILE'], 'rt').read()
        ca_key_file = open(config['CONFIG_SSL_CACERT_KEY_FILE'], 'rt').read()
        ca_key = crypto.load_privatekey(crypto.FILETYPE_PEM, ca_key_file)
        ca = crypto.load_certificate(crypto.FILETYPE_PEM, ca_file)

        k = crypto.PKey()
        k.generate_key(crypto.TYPE_RSA, 4096)
        mail = config['CONFIG_SSL_CERT_SUBJECT_MAIL']
        hostinfo = config['HOST_DETAILS'][host]
        fqdn = hostinfo['fqdn']
        cert = crypto.X509()
        subject = cert.get_subject()
        subject.C = config['CONFIG_SSL_CERT_SUBJECT_C']
        subject.ST = config['CONFIG_SSL_CERT_SUBJECT_ST']
        subject.L = config['CONFIG_SSL_CERT_SUBJECT_L']
        subject.O = config['CONFIG_SSL_CERT_SUBJECT_O']
        subject.OU = config['CONFIG_SSL_CERT_SUBJECT_OU']
        cn = "%s/%s" % (service, fqdn)
        # if subject.CN is more than 64 chars long, cert creation will fail
        if len(cn) > 64:
            cn = cn[0:63]
        subject.CN = cn
        subject.emailAddress = mail

        cert.add_extensions([
            crypto.X509Extension(
                "keyUsage".encode('ascii'),
                False,
                "nonRepudiation,digitalSignature,keyEncipherment".encode('ascii')),
            crypto.X509Extension(
                "extendedKeyUsage".encode('ascii'),
                False,
                "clientAuth,serverAuth".encode('ascii')),
        ])

        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(315360000)
        cert.set_issuer(ca.get_subject())
        cert.set_pubkey(k)
        serial = int(time())
        cert.set_serial_number(serial)
        cert.sign(ca_key, 'sha1')

        final_cert = crypto.dump_certificate(crypto.FILETYPE_PEM, cert)
        final_key = crypto.dump_privatekey(crypto.FILETYPE_PEM, k)
        deliver_ssl_file(ca_file, config['CONFIG_SSL_CACERT'], host)
        deliver_ssl_file(final_cert.decode(), ssl_cert_file, host)
        deliver_ssl_file(final_key.decode(), ssl_key_file, host)

        with open(local_cert_path, 'w') as f:
            f.write(final_cert.decode())


def deliver_ssl_file(content, path, host):
    server = utils.ScriptRunner(host)
    server.append("grep -- '{content}' {path} || "
                  "echo '{content}' > {path} ".format(
                      content=content,
                      path=path))
    server.execute()


def gethostlist(CONF):
    hosts = []
    for key, value in CONF.items():
        if key.endswith("_HOST"):
            value = value.split('/')[0]
            if value and value not in hosts:
                hosts.append(value)
        if key.endswith("_HOSTS"):
            for host in value.split(","):
                host = host.strip()
                host = host.split('/')[0]
                if host and host not in hosts:
                    hosts.append(host)
    return hosts
