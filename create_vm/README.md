# Роль: create_vm

Эта роль создает виртуальную машину в oVirt на основе заданного шаблона, настраивает параметры CPU, RAM, дисков и сети, а также применяет настройки cloud-init для первичной инициализации ВМ.

## Требования

- Ansible версии 2.9 или выше.
- Модуль `ovirt_vm` должен быть установлен.
- Доступ к oVirt API с правами администратора.

## Переменные

| Переменная                  | Описание                                   | Пример значения            |
|-----------------------------|-------------------------------------------|----------------------------|
| `ovirt_url`                 | URL oVirt Engine                          | `https://ovirt-engine.example.com/ovirt-engine/api` |
| `ovirt_username`            | Имя пользователя                          | `admin@internal`           |
| `ovirt_password`            | Пароль пользователя                       | `your_password`            |
| `ovirt_ca_file`             | Путь к CA-сертификату                     | `/etc/pki/ovirt-engine/ca.pem` |
| `vm_name`                   | Имя создаваемой ВМ                        | `example-vm`               |
| `vm_template`               | Шаблон для создания ВМ                    | `template-centos7`         |
| `vm_cluster`                | Кластер, в котором будет создана ВМ       | `Default`                  |
| `vm_memory`                 | Объем оперативной памяти                  | `4GiB`                     |
| `vm_cpu_cores`              | Количество ядер CPU                       | `2`                        |
| `vm_disk_size`              | Размер диска                              | `20GiB`                    |
| `vm_network`                | Сеть для ВМ                               | `ovirtmgmt`                |
| `vm_state`                  | Состояние ВМ после создания               | `running`                  |
| `cloud_init_dns_servers`    | DNS-серверы                               | `8.8.8.8`                  |
| `cloud_init_dns_search`     | DNS-домен                                 | `example.com`              |
| `cloud_init_nic_boot_protocol` | Протокол загрузки NIC                  | `static`                   |
| `cloud_init_nic_ip_address` | IP-адрес NIC                              | `192.168.1.10`             |
| `cloud_init_nic_netmask`    | Маска подсети                             | `255.255.255.0`            |
| `cloud_init_nic_gateway`    | Шлюз                                      | `192.168.1.1`              |
| `cloud_init_nic_name`       | Имя сетевого интерфейса                   | `enp1s0`                   |
| `cloud_init_host_name`      | Полное доменное имя ВМ                    | `vm.example.com`           |
| `cloud_init_user_name`      | Имя пользователя                          | `test`                     |
| `cloud_init_root_password`  | Пароль root                               | `some_pass123`             |
| `cloud_init_custom_script`  | Пользовательский скрипт                   | `touch /etc/cloud/cloud-init.disabled && systemctl disable --now cloud-init` |

## Пример использования

```yaml
- hosts: localhost
  roles:
    - role: create_vm
      vars:
        ovirt_url: "https://ovirt-engine.example.com/ovirt-engine/api"
        ovirt_username: "admin@internal"
        ovirt_password: "your_password"
        vm_name: "my-new-vm"
        vm_template: "template-centos7"
        vm_memory: "8GiB"
        vm_cpu_cores: 4
        cloud_init_nic_ip_address: "192.168.1.10"
        cloud_init_nic_netmask: "255.255.255.0"
        cloud_init_nic_gateway: "192.168.1.1"
        cloud_init_host_name: "my-new-vm.example.com"
        cloud_init_user_name: "admin"
        cloud_init_root_password: "secure_password"
