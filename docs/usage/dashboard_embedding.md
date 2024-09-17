The SDK provides a convenience class for generating the url to embed dashboards in external pages and signing it.
For more information on the options see the [Omni Docs](https://docs.omni.co/docs/embed/private-embedding#embed-url-customization-options).

## Creating the embedder
Configuration of the client can be handled using kwargs or environment variables. There is also the option to create
the embedder using your organization name or a vanity domain, more info on these options is below.

```python title="Kwarg Configuration - Organization Name"
from omni import OmniDashboardEmbedder

embedder = OmniDashboardEmbedder(organization_name="acme", embed_secret="vglUd1WblfyBSdBSMPj0KrxZcNUEZ1CC")
```

```python  title="Kwarg Configuration - Vanity Domain"
from omni import OmniDashboardEmbedder

embedder = OmniDashboardEmbedder(vanity_domain="acme.example.com", embed_secret="vglUd1WblfyBSdBSMPj0KrxZcNUEZ1CC")
```


```python title="Environment Variable Configuration - Organization Name"
import os
from omni import OmniDashboardEmbedder

# For demonstration purposes only. The assumption is that these env vars are already set.
os.environ["OMNI_ORGANIZATION_NAME"] = "acme"
os.environ["OMNI_EMBED_SECRET"] = "vglUd1WblfyBSdBSMPj0KrxZcNUEZ1CC"

embedder = OmniDashboardEmbedder()
```

```python title="Environment Variable Configuration - Vanity Domain"
import os
from omni import OmniDashboardEmbedder

# For demonstration purposes only. The assumption is that these env vars are already set.
os.environ["OMNI_VANITY_DOMAIN"] = "acme.example.com"
os.environ["OMNI_EMBED_SECRET"] = "vglUd1WblfyBSdBSMPj0KrxZcNUEZ1CC"

embedder = OmniDashboardEmbedder()
```

## Generating a dashboard embedding URL.
The embedder object has a single method that generates an embedding url and signs it. For more information on the
options available please see the [API Documentation](../api/OmniDashboardEmbedder.md#omni.OmniDashboardEmbedder.build_url) for the class.

```python
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

The OmniDashboardEmbedder can be instantiated using either the `organization_name` or `vanity_domain` kwargs.
Instantiating with `organization_name` uses the standard Omni endpoint for the embedded dashboard URL. Alternatively,
Omni supports configuring a vanity domain to host embedded dashboards. You can learn about its advantages and setup
instructions [here](https://docs.omni.co/docs/embed/private-embedding#use-a-vanity-domain). Once your vanity domain is
set up, you can instantiate the OmniDashboardEmbedder with it to generate the correct URLs.

## Generating Filter Search Params

!!! note
    Support for dynamically generating filter search parameters is in early development and currently supports a
    limited set of filtering options. If you need specific filters that are not yet available, please create an issue.

Omni dashboard embedding allows passing filter values in the query string for the embedded dashboard. These filters are
represented as complex JSON-encoded strings. If the filter values you want to set are static, you can simply copy the
query string value from the example above.

For dynamically generating filter sets, the SDK provides a helper class, `OmniFilterSet`. This class is designed to
translate simplified query string parameters from your application's requests into the correct Omni format.

### Example: Generating filter search params in a Flask API view

The following example demonstrates how a Flask API view can generate a signed Omni embed URL. It defines a set of
filters and uses the query string arguments from the request to create the appropriate filter search parameters for the
embedded dashboard URL. Using the same names for the query string params and filter names in the `OmniFilterSet`
allows you to pass the Flask `requests.args` directly.

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

- Name of the Omni field to be filtered. Generally a dot-path representing a dimension in a view.
- You must have already created a filter for this field in the Omni dashboard to be embedded.

**`type`**

- Value type of the filter.
- Must pass an option from the OmniFilterDefinition.Type enum.
- Currently supported types - `number` and `string`


**`operator`**

- Type of filter operation to perform.
- Defaults to EQUALS.
- Must pass an option from the OmniFilterDefinition.Operator enum.
- Currently supported operators - `equals`, `less_than`, `greater_than`, `greater_than_or_equal`, `less_than_or_equal`, `between`, `contains`, `starts_with`, `ends_with`


In Omni, not all types support all operators. While there are no conflicts with the currently limited set of supported
types and operators, this may change as more are added.

The following types are supported for `number`:

- ✅ Equals
- ✅ Less than
- ✅ Less than or equal
- ✅ Greater than
- ✅ Greater than or equal
- ✅ Between

The following types are supported for `string`:

- ✅ Equals
- ✅ Contains
- ✅ Starts with
- ✅ Ends with
