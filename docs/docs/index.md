# Omni SDK

**Unofficial  SDK for [Omni Analytics](https://omni.co/)**

## Getting Started

### Install

#### pip

`pip install omni-analytics-sdk`

#### poetry

`poetry add omni-analytics-sdk`

## Configuration

The following environment variables can be set to automatically configure classes so that kwargs do not need to be pass on creation. If you use `OMNI_VANITY_DOMAIN`, you do not need to configure an `OMNI_ORGANIZATION_NAME`.

| Env Var | Description | Example |
| --- | --- | --- |
| OMNI_ORGANIZATION_NAME | Name of your Omni organization. Can be found in Admin -> Settings -> General in the Omni UI | acme |
| OMNI_VANITY_DOMAIN | Vanity Domain for your Omni instance. | reporting.example.com |
| OMNI_EMBED_SECRET | Secret key for created dashboard embed urls. Can be found in Admin -> Embed -> Admin. | vglUd1WblfyBSdBSMPj0KrxZcNUEZ1CC |

## Usage

### Create dashboard embed URLs
The SDK provides a convenience class for generating the url to embed dashboards in external pages and signing it.
For more information on the options see the [Omni Docs](https://docs.omni.co/docs/embed/private-embedding#embed-url-customization-options).

```python
from omni import OmniDashboardEmbedder

# kwargs can be skipped if env vars have been configured.
embedder = OmniDashboardEmbedder(organization_name="acme", embed_secret="vglUd1WblfyBSdBSMPj0KrxZcNUEZ1CC")

url = embedder.build_url(
    content_path="/dashboards/da24491e",
    external_id="1",
    name="Somebody",
    custom_theme={
        "dashboard-background": "#00FF00",
        "dashboard-tile-background": "#00FF00",
    },
    entity="Acme",
    filter_search_params={"state": "GA"},
    link_access=True,
    prefers_dark=OmniDashboardEmbedder.PrefersDark.yes,
    theme=OmniDashboardEmbedder.Theme.dawn,
    user_attributes={"country": "USA"},
)
```