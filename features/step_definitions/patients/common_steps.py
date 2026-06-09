from pytest_bdd import given, parsers, when


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
    assert response.status_code == 200
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
