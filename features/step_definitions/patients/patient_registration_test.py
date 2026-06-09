from pytest_bdd import scenarios, given, when, then, parsers

scenarios("../../specs/patients/patient-registration.feature")


@given(parsers.parse('a patient with email "{email}" already exists'))
def a_patient_with_email_already_exists(client, context, email):
    response = client.post(
        "/api/patients",
        headers={"Authorization": f"Bearer {context['accessToken']}"},
        json={"name": "Existing Patient", "dateOfBirth": "1990-01-01", "email": email},
    )
    assert response.status_code == 201


@when("I register a patient with the following details:")
def register_patient_with_details(context, client, datatable):
    data = {row[0]: row[1] for row in datatable}
    headers = {}
    if "accessToken" in context:
        headers["Authorization"] = f"Bearer {context['accessToken']}"
    context["response"] = client.post("/api/patients", json=data, headers=headers)


@then("the response body should contain the patient ID")
def response_body_should_contain_patient_id(context):
    body = context["response"].json()
    assert body.get("id") not in (None, ""), (
        f"Expected response to contain a patient ID but got: {body}"
    )
    context["patientId"] = body["id"]


@then("I should see the patient profile with the following details:")
def should_see_patient_profile_with_details(context, client, datatable):
    response = client.get(
        f"/api/patients/{context['patientId']}",
        headers={"Authorization": f"Bearer {context['accessToken']}"},
    )
    assert response.status_code == 200
    body = response.json()
    for row in datatable:
        field, expected = row[0], row[1]
        if expected == "<present>":
            assert body.get(field) not in (None, ""), (
                f"Expected patient.{field} to be present but got {body.get(field)!r}"
            )
        else:
            assert body.get(field) == expected, (
                f"Expected patient['{field}'] == '{expected}', got '{body.get(field)}'"
            )


@then("the response body should contain an error indicating the patient email is taken")
def response_body_should_contain_error_patient_email_taken(context):
    body = context["response"].json()
    assert (
        body.get("type") == "https://my-api-doc.dev/problems/patient-already-exists"
    ), (
        f'Expected "type" to be "https://my-api-doc.dev/problems/patient-already-exists". Body: {body}'
    )
