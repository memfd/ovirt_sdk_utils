from ovirtsdk4 import Connection, types
import csv
import logging
import matplotlib.pyplot as plt
import argparse

# Config connection to oVirt API
OVIRT_URL = "https://ovirt-engine.example.com/ovirt-engine/api"
OVIRT_USERNAME = "admin@internal"
OVIRT_PASSWORD = "your_password"
#OVIRT_CA_FILE = "/path/to/ca.crt"

# Config logging
LOG_FILE = "ovirt_script.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# File with VLAN names
VLAN_FILE = "vlan_list.txt"

# Output files
OUTPUT_CSV = "vm_network_mapping.csv"
OUTPUT_IMAGE_PIE = "vm_distribution_vlan_pie.png"
OUTPUT_IMAGE_BAR = "vm_distribution_vlan_bar.png"

def connect_to_ovirt():
    """Create connection to oVirt API."""
    try:
        logging.info("Connecting to oVirt API...")
        connection = Connection(
            url=OVIRT_URL,
            username=OVIRT_USERNAME,
            password=OVIRT_PASSWORD,
            #ca_file=OVIRT_CA_FILE,
            insecure=True
        )
        logging.info("Successfully connected to oVirt API.")
        return connection
    except Exception as e:
        logging.error(f"Failed to connect to oVirt API: {e}")
        raise

def read_vlan_list(vlan_file):
    """Reading VLAN list from a file."""
    try:
        with open(vlan_file, "r", encoding="utf-8") as file:
            vlan_list = [line.strip() for line in file if line.strip()]
        logging.info(f"Read {len(vlan_list)} VLANs from file: {vlan_list}")
        return vlan_list
    except Exception as e:
        logging.error(f"Failed to read VLAN list from file: {e}")
        return []

def get_all_networks(connection):
    """Getting a list of all networks (VLAN)."""
    try:
        logging.info("Retrieving all networks...")
        networks_service = connection.system_service().networks_service()
        networks = networks_service.list()
        network_dict = {network.name: network.id for network in networks}
        logging.info(f"Found {len(network_dict)} networks: {list(network_dict.keys())}")
        return network_dict
    except Exception as e:
        logging.error(f"Failed to retrieve networks: {e}")
        return {}

def get_filtered_networks(connection, vlan_list):
    """Getting a list of networks (VLAN) from a given list."""
    try:
        logging.info("Retrieving filtered networks...")
        networks_service = connection.system_service().networks_service()
        networks = networks_service.list()
        network_dict = {
            network.name: network.id for network in networks if network.name in vlan_list
        }
        logging.info(f"Found {len(network_dict)} matching networks: {list(network_dict.keys())}")
        return network_dict
    except Exception as e:
        logging.error(f"Failed to retrieve filtered networks: {e}")
        return {}

def get_vms_with_networks(connection, networks):
    """Getting a VM list and their network interfaces."""
    vm_network_mapping = {network_name: [] for network_name in networks.keys()}
    try:
        logging.info("Retrieving VMs and their NICs...")
        vms_service = connection.system_service().vms_service()
        vms = vms_service.list()
        logging.info(f"Found {len(vms)} VMs.")

        # Get all VNIC profiles in advance
        vnic_profiles_service = connection.system_service().vnic_profiles_service()
        vnic_profiles = {profile.id: profile for profile in vnic_profiles_service.list()}
        logging.info(f"Retrieved {len(vnic_profiles)} vNIC profiles.")

        for vm in vms:
            logging.debug(f"Processing VM: {vm.name} (ID: {vm.id})")
            vm_service = vms_service.vm_service(vm.id)
            nics_service = vm_service.nics_service()
            nics = nics_service.list()

            if not nics:
                logging.warning(f"No NICs found for VM: {vm.name}")

            for nic in nics:
                logging.debug(f"Processing NIC: {nic.name} (ID: {nic.id}) for VM: {vm.name}")
                if hasattr(nic, 'vnic_profile') and nic.vnic_profile:
                    vnic_profile_id = nic.vnic_profile.id
                    logging.debug(f"NIC {nic.name} has vNIC Profile ID: {vnic_profile_id}")

                    # Check if there is a VNIC profile in the list
                    if vnic_profile_id in vnic_profiles:
                        vnic_profile = vnic_profiles[vnic_profile_id]
                        if hasattr(vnic_profile, 'network') and vnic_profile.network:
                            network_id = vnic_profile.network.id
                            logging.debug(f"vNIC Profile {vnic_profile_id} is associated with Network ID: {network_id}")

                            # Link the network with VM
                            for network_name, network_id_in_dict in networks.items():
                                if network_id == network_id_in_dict:
                                    logging.info(f"VM {vm.name} is associated with network: {network_name}")
                                    vm_network_mapping[network_name].append(vm.name)
                                    break
                        else:
                            logging.warning(f"vNIC Profile {vnic_profile_id} has no associated network for NIC: {nic.name}")
                    else:
                        logging.warning(f"vNIC Profile {vnic_profile_id} not found in retrieved profiles for NIC: {nic.name}")
                else:
                    logging.warning(f"NIC {nic.name} has no vnic_profile for VM: {vm.name}")

    except Exception as e:
        logging.error(f"Failed to retrieve VMs or their networks: {e}")
    return vm_network_mapping

def export_to_csv(vm_network_mapping, output_file):
    """Export to CSV-file."""
    try:
        logging.info("Exporting data to CSV...")
        with open(output_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Network (VLAN)", "VMs"])
            for network_name, vm_list in vm_network_mapping.items():
                writer.writerow([network_name, ", ".join(vm_list) if vm_list else "No VMs"])
        logging.info(f"Data successfully exported to {output_file}")
    except Exception as e:
        logging.error(f"Failed to export data to CSV: {e}")

# // Not used! Do not use a function for a large number of networks //
def visualize_data_pie(vm_network_mapping, output_image):
    """Data visualization in the form of a circular diagram."""
    try:
        logging.info("Creating pie chart visualization...")
        labels = []
        sizes = []

        for network_name, vm_list in vm_network_mapping.items():
            labels.append(network_name)
            sizes.append(len(vm_list))

        # Create a circular diagram
        plt.figure(figsize=(12, 12))
        plt.pie(
            sizes,
            labels=labels,
            autopct='%1.1f%%',
            startangle=140,
            textprops={'fontsize': 8}
        )
        plt.title("Distribution of VMs across VLANs", fontsize=14)
        plt.axis('equal')
        plt.savefig(output_image, bbox_inches='tight')
        logging.info(f"Pie chart visualization saved to {output_image}")
        plt.close()
    except Exception as e:
        logging.error(f"Failed to create pie chart visualization: {e}")

def visualize_data_bar(vm_network_mapping, output_image):
    """Visualization of data in the form of a column diagram."""
    try:
        logging.info("Creating bar chart visualization...")
        networks = []
        vm_counts = []

        for network_name, vm_list in vm_network_mapping.items():
            if vm_list:  # Only networks with at least one VM
                networks.append(network_name)
                vm_counts.append(len(vm_list))

        total_vms = sum(vm_counts)  # The total amount of VM

        # Create a column diagram
        plt.figure(figsize=(10, 6))
        plt.bar(networks, vm_counts, color='skyblue', edgecolor='black')
        plt.xlabel("Networks (VLANs)", fontsize=12)
        plt.ylabel("Number of VMs", fontsize=12)
        plt.title("Number of VMs per VLAN", fontsize=14)
        plt.xticks(rotation=45, ha='right', fontsize=10)  # 45 degrees for better readability
        plt.tight_layout()

        # Add the total amount of VM to the left lower corner
        plt.text(0, -0.35, f"Total VMs: {total_vms}", transform=plt.gca().transAxes, fontsize=10, fontweight='bold')

        # Save the diagram to the file
        plt.savefig(output_image, bbox_inches='tight')
        logging.info(f"Bar chart visualization saved to {output_image}")
        plt.close()
    except Exception as e:
        logging.error(f"Failed to create bar chart visualization: {e}")

def parse_args():
    """Parsing of command line arguments."""
    parser = argparse.ArgumentParser(description="Retrieve VMs by VLAN and visualize the data.")
    parser.add_argument("--all-networks", action="store_true", help="Process all existing networks in oVirt.")
    return parser.parse_args()

def main():
    # Parse the command line arguments
    args = parse_args()

    # Connect to oVirt
    try:
        connection = connect_to_ovirt()
    except Exception:
        return

    try:
        if args.all_networks:
            # Mode for all networks
            logging.info("Running in --all-networks mode.")
            networks = get_all_networks(connection)
            if not networks:
                logging.error("No networks found. Exiting.")
                return
        else:
            # Mode for networks from file
            logging.info("Running in file-based VLAN mode.")
            vlan_list = read_vlan_list(VLAN_FILE)
            if not vlan_list:
                logging.error("No VLANs found in the input file. Exiting.")
                return
            networks = get_filtered_networks(connection, vlan_list)
            if not networks:
                logging.error("No matching networks found. Exiting.")
                return

        # Getting a VM list and networks
        vm_network_mapping = get_vms_with_networks(connection, networks)

        # Export to CSV
        export_to_csv(vm_network_mapping, OUTPUT_CSV)

        # Visualization of data: column diagram
        visualize_data_bar(vm_network_mapping, OUTPUT_IMAGE_BAR)

    finally:
        # Closing connection
        connection.close()
        logging.info("Connection to oVirt API closed.")

if __name__ == "__main__":
    main()
