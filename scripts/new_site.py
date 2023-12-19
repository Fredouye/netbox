from extras.scripts import *
from django.utils.text import slugify

from dcim.choices import DeviceStatusChoices, SiteStatusChoices
from dcim.models import Device, DeviceRole, DeviceType, Site


class NouveauSite(Script):

    class Meta:
        name = "Nouveau site"
        description = "Provisionne un nouveau site"

    site_name = StringVar(
        description="Non du nouveau site"
    )
    switch_count = IntegerVar(
        description="Nombre de switches à créer"
    )
    switch_model = ObjectVar(
        description="Modèle de switch",
        model=DeviceType
    )
    router_count = IntegerVar(
        description="Nombre de firewalls à créer"
    )
    router_model = ObjectVar(
        description="Modèle de firewall",
        model=DeviceType
    )
    server_count = IntegerVar(
        description="Nombre de serveurs à créer"
    )
    server_model = ObjectVar(
        description="Modèle de serveur",
        model=DeviceType
    )

    def run(self, data, commit):

        # Create the new site
        site = Site(
            name=data['site_name'],
            slug=slugify(data['site_name']),
            status=SiteStatusChoices.STATUS_PLANNED
        )
        site.save()
        self.log_success(f"Created new site: {site}")

        # Create access switches
        switch_role = DeviceRole.objects.get(name='Switch')
        for i in range(1, data['switch_count'] + 1):
            switch = Device(
                device_type=data['switch_model'],
                name=f'{site.slug.upper()}-SWITCH-{i}',
                site=site,
                status=DeviceStatusChoices.STATUS_PLANNED,
                device_role=switch_role
            )
            switch.save()
            self.log_success(f"Created new switch: {switch}")

        # Create routers
        router_role = DeviceRole.objects.get(name='Firewall')
        for i in range(1, data['router_count'] + 1):
            router = Device(
                device_type=data['router_model'],
                name=f'{site.slug.upper()}-FIREWALL-{i}',
                site=site,
                status=DeviceStatusChoices.STATUS_PLANNED,
                device_role=router_role
            )
            router.save()
            self.log_success(f"Created new router: {router}")
       
        # Create Servers
        server_role = DeviceRole.objects.get(name='Server')
        for i in range(1, data['server_count'] + 1):
            server = Device(
                device_type=data['server_model'],
                name=f'{site.slug.upper()}-ESX-{i}',
                site=site,
                status=DeviceStatusChoices.STATUS_PLANNED,
                device_role=server_role
            )
            server.save()
            self.log_success(f"Created new server: {server}")

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
