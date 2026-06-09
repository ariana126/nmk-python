from datetime import datetime, timezone
from pytest_bdd import given, parsers, scenarios, then, when

scenarios("../../specs/patients/vitals-recording.feature")


def _parse_value(v: str):
    try:
        return int(v)
    except ValueError:
        try:
            return float(v)
        except ValueError:
            return v


@given(parsers.parse('a patient exists with ID "{patient_id_key}"'))
def a_patient_exists(context, client, patient_id_key):
    response = client.post(
        "/api/patients",
        headers={"Authorization": f"Bearer {context['accessToken']}"},
        json={
            "name": "Test Patient",
            "dateOfBirth": "1990-01-01",
            "email": f"{patient_id_key}@test.com",
        },
    )
    assert response.status_code == 201
    context[patient_id_key] = response.json()["id"]


@when(
    parsers.parse(
        'I record vitals for the patient with ID "{patient_id_key}" with the following details:'
    )
)
def record_vitals(context, client, patient_id_key, datatable):
    actual_id = context.get(patient_id_key, patient_id_key)
    context["last_vitals_patient_id"] = actual_id
    body = {row[0]: _parse_value(row[1]) for row in datatable}
    headers = {}
    if "accessToken" in context:
        headers["Authorization"] = f"Bearer {context['accessToken']}"
    context["response"] = client.post(
        f"/api/patients/{actual_id}/vitals", json=body, headers=headers
    )


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
