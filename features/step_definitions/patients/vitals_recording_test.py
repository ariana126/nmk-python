from datetime import datetime, timezone
from pytest_bdd import scenarios, then

scenarios("../../specs/patients/vitals-recording.feature")


@then(
    "I should see a new record at the top of the patient's vitals with the following details:"
)
def see_new_vitals_record(context, client, datatable):
    response = client.get(
        f"/api/patients/{context['last_vitals_patient_id']}/vitals",
        headers={"Authorization": f"Bearer {context['accessToken']}"},
    )
    assert response.status_code == 200
    vitals = response.json()
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
