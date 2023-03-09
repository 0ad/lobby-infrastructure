# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "debian/testing64"  # TODO: change to bookworm64 once available

  config.vm.hostname = "lobby"

  config.vm.provision "ansible" do |ansible|
    ansible.galaxy_command = "ansible-galaxy install --role-file=%{role_file}"
    ansible.galaxy_role_file = "requirements.yml"
    ansible.raw_arguments = ["--diff", "--extra-vars", "is_vagrant=true"]
    ansible.playbook = "site.yml"
  end

  config.vm.network "forwarded_port", guest: 5222, host: 5222
end
