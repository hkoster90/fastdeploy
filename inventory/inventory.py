from typing import List, Dict, Optional
from pymongo import MongoClient
from .models import Host, HostGroup, Variable


class DuplicateHostnameError(Exception):
    """Exception raised for duplicate hostnames in the inventory."""

    def __init__(self, hostname: str):
        self.hostname = hostname
        super().__init__(f"Hostname(s) '{hostname}' already exists in the inventory.")


class InventoryManager:
    def __init__(self, db_url: str, db_name: str, db_collection: str):
        self.client = MongoClient(db_url)
        self.db = self.client[db_name]
        self.collection = self.db[db_collection]

    def is_duplicate_hostname(self, hostname: str) -> bool:
        """Check if a hostname already exists in the inventory.

        Args:
            hostname (str): The hostname to check.

        Returns:
            bool: True if the hostname exists, False otherwise.
        """
        return self.collection.count_documents({'hostname': hostname}) > 0

    def add_host(self, host: Host) -> None:
        """Add a host to the inventory.

        Args:
            host (Host): The host object representing the host to add.

        Raises:
            DuplicateHostnameError: If the hostname already exists in the inventory.
        """
        if self.is_duplicate_hostname(host.hostname):
            raise DuplicateHostnameError(host.hostname)

        host_data = {
            'hostname': host.hostname,
            'ip_address': host.ip_address,
            'password': host.encrypt_password(),
            'private_key_path': host.private_key_path,
            'groups': [],
            'variables': {}
        }
        self.collection.insert_one(host_data)

    def add_hosts(self, hosts: List[Host]) -> None:
        """Add multiple hosts to the inventory.

        Args:
            hosts (List[Host]): List of host objects representing the hosts to add.

        Raises:
            DuplicateHostnameError: If any of the hostnames already exist in the inventory.
        """
        duplicate_hostnames = []
        hostnames = []
        for host in hosts:
            if self.is_duplicate_hostname(host.hostname):
                duplicate_hostnames.append(host.hostname)
            else:
                host_data = {
                    'hostname': host.hostname,
                    'ip_address': host.ip_address,
                    'password': host.encrypt_password(),
                    'private_key_path': host.private_key_path,
                    'groups': [],
                    'variables': {}
                }
                hostnames.append(host_data)

        if hostnames:
            self.collection.insert_many(hostnames)

        if duplicate_hostnames:
            raise DuplicateHostnameError(', '.join(duplicate_hostnames))

    def update_host(self, hostname: str, new_data: Dict) -> None:
        """Update a host in the inventory.

        Args:
            hostname (str): The hostname of the host to update.
            new_data (Dict): The new data to update.
        """
        self.collection.update_one({'hostname': hostname}, {'$set': new_data})

    def delete_host(self, hostname: str) -> None:
        """Delete a host from the inventory.

        Args:
            hostname (str): The hostname of the host to delete.
        """
        self.collection.delete_one({'hostname': hostname})

    def get_host_by_name(self, hostname: str, decrypt_password: bool = False) -> Optional[Host]:
        """Retrieve a host by its hostname.

        Args:
            hostname (str): The hostname of the host.
            decrypt_password (bool): Whether to decrypt the password or not.

        Returns:
            Optional[Host]: The host object if found, None otherwise.
        """
        host_data = self.collection.find_one({'hostname': hostname})
        if host_data:
            return Host(
                host_data['hostname'],
                host_data['ip_address'],
                host_data['password'],
                host_data['private_key_path']
            )
        return None

    def get_hosts(self, decrypt_password: bool = False) -> List[Host]:
        """Retrieve all hosts from the inventory.

        Args:
            decrypt_password (bool): Whether to decrypt passwords or not.

        Returns:
            List[Host]: List of all hosts in the inventory.
        """
        hosts = self.collection.find()
        host_list = []
        for host in hosts:
            host_list.append(
                Host(
                    host['hostname'],
                    host['ip_address'],
                    host['password'],
                    host['private_key_path']
                )
            )
        return host_list

    def add_group(self, group: HostGroup) -> None:
        """Add a group to the inventory.

        Args:
            group (HostGroup): The group object representing the group to add.

        Raises:
            ValueError: If the group name already exists in the inventory.
        """
        if self.get_group_by_name(group.group_name):
            raise ValueError(f"Group '{group.group_name}' already exists in the inventory.")

        group_data = {
            'group_name': group.group_name,
            'description': group.description
        }
        self.collection.insert_one(group_data)

    def delete_group(self, group_name: str) -> None:
        """Delete a group from the inventory.

        Args:
            group_name (str): The name of the group to delete.
        """
        self.collection.delete_one({'group_name': group_name})

    def update_group(self, group_name: str, new_data: Dict) -> None:
        """Update a group in the inventory.

        Args:
            group_name (str): The name of the group to update.
            new_data (Dict): The new data to update.
        """
        self.collection.update_one({'group_name': group_name}, {'$set': new_data})

    def get_group_by_name(self, group_name: str) -> Optional[HostGroup]:
        """Retrieve a group by its name.

        Args:
            group_name (str): The name of the group.

        Returns:
            Optional[HostGroup]: The group object if found, None otherwise.
        """
        group_data = self.collection.find_one({'group_name': group_name})
        if group_data:
            return HostGroup(group_data['group_name'], group_data['description'])
        return None

    def get_groups(self) -> List[HostGroup]:
        """Retrieve all groups from the inventory.

        Returns:
            List[HostGroup]: List of all groups in the inventory.
        """
        groups = self.collection.find()
        return [HostGroup(group['group_name'], group['description']) for group in groups]

    def add_variable(self, variable: Variable) -> None:
        """Add a variable to the inventory.

        Args:
            variable (Variable): The variable object representing the variable to add.
        """
        variable_data = {
            'variable_name': variable.variable_name,
            'value': variable.value
        }
        self.collection.insert_one(variable_data)

    def delete_variable(self, variable_name: str) -> None:
        """Delete a variable from the inventory.

        Args:
            variable_name (str): The name of the variable to delete.
        """
        self.collection.delete_one({'variable_name': variable_name})

    def update_variable(self, variable_name: str, new_data: Dict) -> None:
        """Update a variable in the inventory.

        Args:
            variable_name (str): The name of the variable to update.
            new_data (Dict): The new data to update.
        """
        self.collection.update_one({'variable_name': variable_name}, {'$set': new_data})

    def get_variable_by_name(self, variable_name: str) -> Optional[Variable]:
        """Retrieve a variable by its name.

        Args:
            variable_name (str): The name of the variable.

        Returns:
            Optional[Variable]: The variable object if found, None otherwise.
        """
        variable_data = self.collection.find_one({'variable_name': variable_name})
        if variable_data:
            return Variable(variable_data['variable_name'], variable_data['value'])
        return None

    def get_variables(self) -> List[Variable]:
        """Retrieve all variables from the inventory.

        Returns:
            List[Variable]: List of all variables in the inventory.
        """
        variables = self.collection.find()
        return [Variable(variable['variable_name'], variable['value']) for variable in variables]
