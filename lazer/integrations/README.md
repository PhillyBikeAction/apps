## Submit PPA Smartsheet

### Usage
Example:
```python
from datetime import datetime, UTC
from django.core.files.base import ContentFile
from lazer.integrations.submit_form import MobilityAccessViolation, submit_form_with_playwright
# could also import enums and use directly, otherwise closest text match is selected
# from lazer.integrations.submit_form import ViolationObserved, OccurrenceFrequency, VehicleType, VehicleColor

violation = MobilityAccessViolation(
    date_time_observed=datetime.now(UTC),
    vehicle_color = "black",
    make="hyundai",
    body_style="sedan",
    violation_observed="bike lane",
    address = "2000 Market St, Philadelphia, PA 19103, USA",
)
photo: str | ContentFile = "local_picture_or_content_file.jpg"
await submit_form_with_playwright(violation, photo)
```

### Details

The `submit_form.py` contains all necessary tools to submit the form to PPA's Smartsheet. It uses Playwright to open a browser with the form.
The form is pre-filled using [Smartsheet query string](https://help.smartsheet.com/articles/2478871-url-query-string-form-default-values).

The form has a few dropdowns that only accept exact values, otherwise pre-fill doesn't work. Those are enums `ViolationObserved`, `OccuranceFrequency`, `VehicleType`, and `VehicleColor`.

The address returned by plate/car recognition API is a full address, while the form accepts "street number", "block", and "zip code". The address is parsed using [pyap2](https://pypi.org/project/pyap2/) (actively maintained fork of `pyap`).

The `MobilityAccessViolation` has a handy `from_json` call that takes in the API returned object.

The form is protected by Google's reCaptcha (v2?). The `playwright-stealth` package helps to avoid any submission issues. For now at least.

> Note: Not sure if the Photo, "Email me with the copy", and the email itself can be pre-filled.

### Debugging form submission

One way for debugging is to define a known, previously unsubmitted violation. For example, you could get one by uploading a photo of a violation from your computed with Developer Tools open.
Then grab the response from the POST to `/submit`. The output is directly compatible with `MobilityAccessViolation.from_json`.

**IMPORTANT: remember to change the address and time of the actual violation in the JSON.**

When you have the model parsed, print it out and make sure the fields make sense.

To play around with form you can call the `submit_form_with_playwright` directly and use `tracing=True` to save traces from the session. Optionally, comment out the "submit" button click, if you're testing the form fill out.

When trace is generated, it would be in the repo root directory like `trace_123456.zip`. Open the trace with `playwright show-trace trace_123456.zip`. [More details about the Playwright Trace Viewer](https://playwright.dev/python/docs/trace-viewer).

For example, if you have a script or Jupyter notebook cell that you're debugging, your code might look like this:

```python
from lazer.integrations.submit_form import MobilityAccessViolation, submit_form_with_playwright

submit_result = {"your": "json", "from": "post to /SUBMIT", "goes": "here"}

# Example usage of MobilityAccessViolation
violation = MobilityAccessViolation.from_json(submit_result)
# VALIDATE the violation fields/parsing
print(violation)

# fill out and submit the form ~4-6 seconds
await submit_form_with_playwright(violation, "real_violation_photo.jpg", "email_is_optional@email.com", tracing=True)
```
