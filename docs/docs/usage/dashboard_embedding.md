The SDK provides a convenience class for generating the url to embed dashboards in external pages and signing it.
For more information on the options see the [Omni Docs](https://docs.omni.co/docs/embed/private-embedding#embed-url-customization-options).

```python
from omni import OmniDashboardEmbedder

# kwargs in OmniDashboardEmbedder constructor are not required if environment variables have been configured.

# Using 'organization_name'
embedder = OmniDashboardEmbedder(organization_name="acme", embed_secret="vglUd1WblfyBSdBSMPj0KrxZcNUEZ1CC")

# Using 'vanity_domain'
embedder = OmniDashboardEmbedder(vanity_domain="acme.example.com", embed_secret="vglUd1WblfyBSdBSMPj0KrxZcNUEZ1CC")

# If all options defined as ENV variables
embedder = OmniDashboardEmbedder()

url = embedder.build_url(
    content_path="/dashboards/da24491e",
    external_id="1",
    name="Somebody",
    custom_theme={
        "dashboard-background": "#00FF00",
        "dashboard-tile-background": "#00FF00",
    },
    entity="Acme",
    link_access=True,
    filter_search_params='f--object.id=%7B"is_inclusive"%3Afalse%2C"is_negative"%3Afalse%2C"kind"%3A"EQUALS"%2C"type"%3A"number"%2C"values"%3A%5B"1"%5D%7D'
    prefers_dark=OmniDashboardEmbedder.PrefersDark.yes,
    theme=OmniDashboardEmbedder.Theme.dawn,
    user_attributes={"country": "USA"},
)
```

## Organization Name vs. Vanity Domain 

The `OmniDashboardEmbedder` can be instantiated using either the `organization_name` or `vanity_domain` kwargs. 
Using `organization_name` results in the standard Omni endpoint being used for the embedded dashboard URL. 
Omni has support for configuring a vanity domain to host the embedded dashboards. You can learn about its advantages 
and instructions for setup [here](https://docs.omni.co/docs/embed/private-embedding#use-a-vanity-domain).
Once your vanity domain is setup you may instantiate the `OmniDashboardEmbedder` with it to generate the correct URLs.

## Generating Filter Search Params

!!! note
    Support for dynamically generating filter search params is in early development and supports a narrow amount of all 
    possible filtering options. Please create an issue if there are specific filters missing that you need.

Omni dashboard embedding supports passing filter values in the query string for the embedded dashboard. These filters are
a complex json encoded string. If the filter values you want to set are static you can simply copy the query string value 
as seen in the example above.

If you need to dynamically generate the filters sets the SDK provides a helper class, `OmniFilterSet`. The class is 
primarily designed to support translating simplified query string params passed in the requests to your application to 
the correct Omni format.

The example below shows what a flask API view that generates a signed Omni embed url might look like. The view defines 
a set filters and then uses the query string args from the request to generate the correct filter search params value 
for the embedded dashboard URL.

```python title="myapp/views.py"
from myapp import app
from flask import request
from omni import OmniDashboardEmbedder, OmniFilterSet, OmniFilterDefinition


@app.route("/omni_dashboard_url/")
def get_omni_dashboard_url():
    filter_set = OmniFilterSet(
        latitude=OmniFilterDefinition(
            field="address.latitude_filter",
            type=OmniFilterDefinition.Type.number,
        ),
        longitude=OmniFilterDefinition(
            field="address.longitude_filter",
            type=OmniFilterDefinition.Type.number,
        ),
        distance=OmniFilterDefinition(
            field="address.distance_selected_to_address_in_miles",
            type=OmniFilterDefinition.Type.number,
            operator=OmniFilterDefinition.Operator.less_than,
        ),
    )

    # Query string for this GET request - ?latitude=33.555&longitude=-117.602&distance=10
    # request.args == {"latitude": 33.555, "longitude": -117.602, "distance": 10}
    filter_search_params = filter_set.get_filter_search_params(request.args)

    embedder = OmniDashboardEmbedder(organization_name="acme", embed_secret="vglUd1WblfyBSdBSMPj0KrxZcNUEZ1CC")
    url = embedder.build_url(
        content_path="/dashboards/da24491e",
        external_id="1",
        name="Somebody",
        filter_search_params=filter_search_params
    )
    return {"url": url}, 200
```

### Defining Filters
To define a filter you instantiate an instance of the `OmniFilterDefinition` class with 3 arguments – field, type, and
operator.

**`field`** 

- Name of the Omni field to be filtered. Generally a dot-path a dimension in a view.
- You must have already created a filter for this field in the Omni dashboard to be embedded.

**`type`**

- Value type of the filter.
- Must pass an option from the OmniFilterDefinition.Type enum.
- Currently supported types - `number`


**`operator`**

- Type of filter option to perform.
- Defaults to EQUALS.
- Must pass an option from the OmniFilterDefinition.Operator enum.
- Currently supported operators - `equals`, `less_than`, `greater_than`


In Omni not all types supports all operators. There are no conflicts with the narrow amount of types and operators
currently supported but that will change soon. Below is a matrix showing compatibility between types and operators.

|         | equals | less_than | greater_than |
|---------|--------|-----------|--------------|
| number  | ✅      |     ✅      |       ✅       |
