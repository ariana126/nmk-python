from datetime import datetime, timezone
from pytest_bdd import scenarios, then, when

scenarios("../../specs/patients/vitals-alerting.feature")


@when("I open the patient's alerting vitals page")
def open_alerting_vitals_page(context, client):
    patient_id = context["last_vitals_patient_id"]
    context["response"] = client.get(
        f"/api/patients/{patient_id}/vitals/alerting",
        headers={"Authorization": f"Bearer {context['accessToken']}"},
    )


@then("I should see a vitals record at the top with the following details:")
def see_vitals_record_at_top(context, datatable):
    vitals = context["response"].json()
    assert len(vitals) > 0, f"Expected at least one vital record but got: {vitals}"
    top = vitals[0]
    for row in datatable:
        field, expected = row[0], row[1]
        if expected == "<past-datetime>":
            dt_str = top.get(field)
            assert dt_str, f"Expected {field} to be present but got: {top}"
            dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            assert dt < datetime.now(timezone.utc), (
                f"Expected {field} to be a past datetime but got: {dt_str}"
            )
        else:
            assert str(top.get(field)) == expected, (
                f"Expected vitals['{field}'] == '{expected}', got '{top.get(field)}'"
            )


@then("the vitals list should be empty")
def vitals_list_should_be_empty(context):
    assert context["response"].json() == [], (
        f"Expected empty vitals list but got: {context['response'].json()}"
    )
