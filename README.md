# Pyrogenesis multiplayer-lobby Infrastructure-as-Code

This repository contains the Ansible playbooks which are used to manage the official multiplayer
lobby for 0ad and which can be used to deploy multiplayer lobbies for any Pyrogenesis based game.

## System requirements

The required resources for lobby servers are pretty low, so you probably want to deploy a lobby to
a virtual machine with resources tailored for it or a small single-board computer like a Raspberry
Pi.

The playbooks in this repository assume that running Pyrogenesis lobbies is the only purpose of the
host they get deployed to. While running additional services on such a system might work fine,
please mind that the playbooks might interfere with that.

The minimum resources for a server to host a single lobby for one version of Pyrogenesis are:

- 1 CPU core
- 512MB RAM
- 5GB storage

More CPU and memory might be necessary when running multiple lobbies for multiple versions of
Pyrogenesis, especially if they're used by many players.

More storage might be necessary if there is a high number of players playing hosted games, as the
utilized storage increases primarily because of system and chat logs.

## Vagrant

For testing purposes you can provision a virtual machine with a complete setup using
[Vagrant](https://www.vagrantup.com/). To do so follow the following steps:

1. Install [Vagrant](https://www.vagrantup.com/)
2. Install [Ansible](https://www.ansible.com/)
3. Run `vagrant up` from the project directory and wait a few minutes, while Vagrant fetches the
   base image from the internet and installs and configures all necessary software.
4. **Back up your existing Pyrogenesis configuration, as the following steps will override the
   stored credentials for the official multiplayer lobby!**
5. Run a Pyrogenesis client like 0 A.D. with the parameters below:

   ```shell
   pyrogenesis \
     -conf=lobby.room:arena \
     -conf=lobby.server:localhost \
     -conf=lobby.xpartamupp:xpartamupp \
     -conf=lobby.echelon:echelon \
     -conf=lobby.verify_certificate:false
   ```

6. In the game create a new multiplayer account. This account will be created on the local lobby
   server.
7. Connect to the multiplayer lobby in game.

## Deployment

As applying the lobby configuration defined in the playbooks in this repository is a delicate
operation and does require SSH-access to the host running the 0ad multiplayer lobby, it's not done
automatically whenever code gets added in the Git repository. Instead, is has to be done manually.

To do so, you need to have [Ansible](https://www.ansible.com/) installed and have SSH-access to the
host supposed to run the multiplayer lobby with a user that has password-less sudo permission. That
host also needs to run Debian 12 (Bookworm) as operating system, as that's the only one we support.
Once you got that in place, follow the steps below to deploy it initially or to deploy any changes.

Updating an existing lobby server is supposed to not interfere running operation, by not restarting
already running services. However, there is no guarantee that this is always the case. This also
means services have to be manually restarted if desired.

Before applying configuration change you need to create an inventory to tell Ansible to which host
to deploy changes to. To do so create a file called `hosts` in the project directory and either
add the full hostname in there or an SSH host alias. A basic configuration could look like this:

```ini
[hosts]
lobby.mygame.tld
```

Ansible also offers options to provide additional connection configuration in such an inventory.
For details please check
"[How to build your inventory](https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html)".
For complex connection properties, like when needing to use an SSH jump host to reach the lobby
server, instead of specifying all of them in the inventory file, it's often easier to do so in the
SSH configuration by defining a host alias.

## Initial setup of a lobby server

1. Create A-records for all domains you plan to serve lobbies for plus `conference`-subdomains for
   them in DNS.
2. Connect via SSH and manually ensure that the `python3` and `python3-apt` packages are installed,
   as they're required for Ansible to run.
3. Configure the `hosts` file, so it matches your SSH config in terms of hostname and username.
4. Create a file called `lobby-config.xml` in the project directory and configure it, so it fits
   your needs.
5. Deploy the lobby:

   ```shell
   ansible-playbook --diff site.yml
   ```

## Update an existing lobby server

1. Configure the `hosts` file, so it matches your SSH config in terms of hostname and username.
2. Fetch the current parameters for the playbooks, which aren't included in the git repository,
   because they contain sensitive data:

   ```shell
   ansible-playbook fetch-config.yml
   ```

3. Change any parameters in `lobby-config.xml` you'd like to change.
4. Check what applying the playbook would change:

   ```shell
   ansible-playbook --diff --check site.yml
   ```

5. Apply changes:

   ```shell
   ansible-playbook --diff site.yml
   ```
