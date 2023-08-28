# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "debian/bookworm64"

  config.vm.provider :virtualbox do |vb|
      vb.memory = 1024
  end

  config.vm.define "lobby-vagrant"
  config.vm.hostname = "lobby-vagrant"

  config.vm.provision "shell",
    inline: "apt-get update; DEBIAN_FRONTEND=noninteractive apt-get install -y acl"

  config.vm.provision "ansible_local" do |ansible|
    ansible.galaxy_command = "ansible-galaxy install --role-file=%{role_file}"
    ansible.galaxy_role_file = "requirements.yml"
    ansible.raw_arguments = ["--diff"]
    ansible.playbook = "site.yml"
  end

  config.vm.network "forwarded_port", guest: 3478, host: 3478, protocol: "udp"
  config.vm.network "forwarded_port", guest: 5222, host: 5222
end
