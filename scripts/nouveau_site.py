from extras.scripts import *
from django.utils.text import slugify

from dcim.choices import DeviceStatusChoices, SiteStatusChoices
from dcim.models import Device, DeviceRole, DeviceType, Site


class NouveauSite(Script):

    class Meta:
        name = "Nouveau site"
        description = "Provisionne un nouveau site"

    nom_du_site = StringVar(
        description="Nom du nouveau site"
    )
    nombre_de_switches = IntegerVar(
        description="Nombre de switches à créer"
    )
    modele_de_switch = ObjectVar(
        description="Modèle de switch",
        model=DeviceType
    )
    nombre_de_firewalls = IntegerVar(
        description="Nombre de firewalls à créer"
    )
    modele_de_firewall = ObjectVar(
        description="Modèle de firewall",
        model=DeviceType
    )
    nombre_de_serveurs = IntegerVar(
        description="Nombre de serveurs à créer"
    )
    modele_de_serveur = ObjectVar(
        description="Modèle de serveur",
        model=DeviceType
    )

    def run(self, data, commit):

        # Create the new site
        site = Site(
            name=data['nom_du_site'],
            slug=slugify(data['nom_du_site']),
            status=SiteStatusChoices.STATUS_PLANNED
        )
        site.save()
        self.log_success(f"Site créé: {site}")

        # Create access switches
        switch_role = DeviceRole.objects.get(name='Switch')
        for i in range(1, data['nombre_de_switches'] + 1):
            switch = Device(
                device_type=data['modele_de_switch'],
                name=f'{site.slug.upper()}-SWITCH-{i}',
                site=site,
                status=DeviceStatusChoices.STATUS_PLANNED,
                device_role=switch_role
            )
            switch.save()
            self.log_success(f"Switch créé: {switch}")

        # Create routers
        router_role = DeviceRole.objects.get(name='Firewall')
        for i in range(1, data['nombre_de_firewalls'] + 1):
            router = Device(
                device_type=data['modele_de_firewall'],
                name=f'{site.slug.upper()}-FIREWALL-{i}',
                site=site,
                status=DeviceStatusChoices.STATUS_PLANNED,
                device_role=router_role
            )
            router.save()
            self.log_success(f"Firewall créé: {router}")
        
        # Create Servers
        server_role = DeviceRole.objects.get(name='Server')
        for i in range(1, data['nombre_de_serveurs'] + 1):
            server = Device(
                device_type=data['modele_de_serveur'],
                name=f'{site.slug.upper()}-ESX-{i}',
                site=site,
                status=DeviceStatusChoices.STATUS_PLANNED,
                device_role=server_role
            )
            server.save()
            self.log_success(f"Serveur créé: {server}")

        # Generate a CSV table of new devices
        output = [
            'name,make,model'
        ]
        for device in Device.objects.filter(site=site):
            attrs = [
                device.name,
                device.device_type.manufacturer.name,
                device.device_type.model
            ]
            output.append(','.join(attrs))

        return '\n'.join(output)
