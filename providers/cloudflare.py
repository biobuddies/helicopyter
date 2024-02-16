from dataclasses import dataclass
from functools import partial
from typing import ClassVar, TypedDict


class Registry:
    def __init__(self, cls):
        self.cls = cls
        self.instances: dict[str, cls] = {}

    def __getattr__(self, name):
        if name in self.instances:
            return self.instances[name]
        return partial(self.cls, self, name)

    def __str__(self):
        return self.cls._str


registries: dict[str, Registry] = {}


@dataclass
class RegisteredDataclass:
    _str: ClassVar[str]
    _registry: Registry
    _name: str

    def __post_init__(self):
        print(f'initializing {self._registry}.{self._name}')
        #registries[]
        self._registry.instances[self._name] = self



@dataclass
class CloudflareRecord(RegisteredDataclass):
    """Provides a Cloudflare record resource."""

    _str: ClassVar[str] = 'cloudflare_record'
    _registry: Registry
    _name: str

    #: The name of the record. **Modifying this attribute will force creation of a new resource.**
    name: str

    #: The type of the record. Available values: `A`, `AAAA`, `CAA`, `CNAME`, `TXT`, `SRV`, `LOC`,
    #: `MX`, `NS`, `SPF`, `CERT`, `DNSKEY`, `DS`, `NAPTR`, `SMIMEA`, `SSHFP`, `TLSA`, `URI`, `PTR`,
    #: `HTTPS`. **Modifying this attribute will force creation of a new resource.**
    type: str

    #: The zone identifier to target for the resource. **Modifying this attribute will force creation
    #: of a new resource.**
    zone_id: str

    #: Allow creation of this record in Terraform to overwrite an existing record, if any. This does
    #: not affect the ability to update the record in Terraform and does not prevent other resources
    #: within Terraform or manual changes outside Terraform from overwriting this record. **This
    #: configuration is not recommended for most environments**. Defaults to `false`.
    allow_overwrite: bool | None = None

    #: Comments or notes about the DNS record. This field has no effect on DNS responses.
    comment: str | None = None

    #: The priority of the record.
    priority: float | None = None

    #: Whether the record gets Cloudflare's origin protection.
    proxied: bool | None = None

    #: Custom tags for the DNS record.
    tags: set[str] | None = None


    @property
    def created_on(self) -> str:
        """The RFC3339 timestamp of when the record was created."""


    @property
    def hostname(self) -> str:
        """The FQDN of the record."""


    @property
    def id(self) -> str:
        pass


    @property
    def metadata(self) -> dict[str]:
        """A key-value map of string metadata Cloudflare associates with the record."""


    @property
    def modified_on(self) -> str:
        """The RFC3339 timestamp of when the record was last modified."""


    @property
    def proxiable(self) -> bool:
        """Shows whether this record can be proxied."""


    @property
    def ttl(self) -> float:
        """The TTL of the record."""


    @property
    def value(self) -> str:
        """The value of the record. Conflicts with `data`."""



cloudflare_record = Registry(CloudflareRecord)
