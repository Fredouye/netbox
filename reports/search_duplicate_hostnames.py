from dcim.models import Device
from ipam.models import IPAddress
from extras.reports import Report
from collections import defaultdict

class HostnameDuplicateReport(Report):
    description = "Check for duplicate DNS names"

    def test_dns_duplicates(self):
        # Utiliser un dictionnaire pour compter les occurrences de chaque dns_name
        dns_name_count = defaultdict(list)

        # Parcourir toutes les adresses IP et collecter les dns_names
        for ip in IPAddress.objects.all():
            if ip.dns_name:
                dns_name_count[ip.dns_name].append(ip)

        # Identifier les doublons et les reporter
        for dns_name, ips in dns_name_count.items():
            if len(ips) > 1:
                self.log_failure(ips[0], f"DNS name '{dns_name}' is duplicated {len(ips)} times: {', '.join(str(ip) for ip in ips)}")
            else:
                self.log_success(ips[0])

# Enregistrement du rapport pour qu'il soit exécutable dans Netbox
HostnameDuplicateReport()
