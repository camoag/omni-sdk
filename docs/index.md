# Omni SDK

**Unofficial  SDK for [Omni Analytics](https://omni.co/)**

## Getting Started

### Installation

#### pip

`pip install omni-analytics-sdk`

#### poetry

`poetry add omni-analytics-sdk`

### Configuration

The following environment variables can be set to automatically configure classes so that kwargs do not need to be passed on instantiation.

| Env Var                | Description                                                                                                                                      | Example                          |
|------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------|
| OMNI_ORGANIZATION_NAME | Name of your Omni organization. Can be found in `Admin -> Settings -> General` in the Omni UI                                                      | acme                             |
| OMNI_VANITY_DOMAIN     | Vanity Domain for your Omni instance. More info on vanity domains [here](https://docs.omni.co/docs/embed/private-embedding#use-a-vanity-domain). | reporting.example.com            |
| OMNI_EMBED_SECRET      | Secret key for created dashboard embed urls. Can be found in `Admin -> Embed -> Admin`.                                                            | vglUd1WblfyBSdBSMPj0KrxZcNUEZ1CC |
| OMNI_API_KEY           | API key for authenticating requests to the REST API. Can be generated in `Admin -> API Keys`.                                                      | omni_osk_r0dvvwTfLkOC1QP6eomT... |

### Usage

Visit the [Dashboard Embedding](usage/dashboard_embedding.md) or [REST API Client](usage/api_client.md) pages for 
usage information.






