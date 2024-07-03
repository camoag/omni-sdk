# Omni SDK

**Unofficial  SDK for [Omni Analytics](https://omni.co/)**

## Getting Started

### Installation

#### pip

`pip install git+https://github.com/tillable/omni-sdk.git`

#### poetry

`poetry add git+https://github.com/tillable/omni-sdk.git`

### Configuration

The following environment variables can be set to automatically configure classes so that kwargs do not need to be pass on creation. If you use `OMNI_VANITY_DOMAIN`, you do not need to configure an `OMNI_ORGANIZATION_NAME`.

| Env Var | Description | Example |
| --- | --- | --- |
| OMNI_ORGANIZATION_NAME | Name of your Omni organization. Can be found in Admin -> Settings -> General in the Omni UI | acme |
| OMNI_VANITY_DOMAIN | Vanity Domain for your Omni instance. | reporting.example.com |
| OMNI_EMBED_SECRET | Secret key for created dashboard embed urls. Can be found in Admin -> Embed -> Admin. | vglUd1WblfyBSdBSMPj0KrxZcNUEZ1CC |

### Usage

Visit the [Dashboard Embedding](usage/dashboard_embedding.md) or [REST API Client](usage/api_client.md) pages for 
usage information.
