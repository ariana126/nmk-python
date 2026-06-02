import pytest
from pytest_bdd import scenarios, given, when, then, parsers

scenarios("../../specs/identity/register.feature")


@given(parsers.parse('no user with email "{email}" exists'))
def no_user_with_email_exists(email):
    pass


@given(parsers.parse('a user with email "{email}" already exists'))
def a_user_with_email_already_exists(client, email):
    response = client.post("/api/users", json={
        "firstName": "Existing",
        "lastName": "User",
        "email": email,
        "password": "ExistingPass123!",
    })
    assert response.status_code == 201


@when("I register with the following details:")
def register_with_details(context, client, datatable):
    data = {row[0]: row[1] for row in datatable}
    context["response"] = client.post("/api/users", json=data)


@then(parsers.parse('I should be able to log in with email "{email}" and password "{password}"'))
def should_be_able_to_log_in(context, client, email, password):
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    context["accessToken"] = response.json()["accessToken"]


@then("I should see my profile with the following details:")
def should_see_profile_with_details(context, client, datatable):
    response = client.get("/api/users/me", headers={"Authorization": f"Bearer {context['accessToken']}"})
    assert response.status_code == 200
    body = response.json()
    body_keys = sorted(body.keys())
    expected_keys = sorted(row[0] for row in datatable)
    assert body_keys == expected_keys, (
        f"Expected profile to contain exactly {expected_keys} but got {body_keys}"
    )
    for row in datatable:
        field, expected = row[0], row[1]
        if expected == "<present>":
            assert body[field] not in (None, ""), (
                f"Expected profile.{field} to be present but got {body[field]!r}"
            )
        else:
            assert body[field] == expected, (
                f"Expected profile['{field}'] == '{expected}', got '{body.get(field)}'"
            )


@then(parsers.parse('I should not be able to log in with email "{email}" and password "{password}"'))
def should_not_be_able_to_log_in(client, email, password):
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 401


@then("the response body should contain an error indicating the email is taken")
def response_body_should_contain_error_email_taken(context):
    body = context["response"].json()
    assert body.get("type") == "https://my-api-doc.dev/problems/user-already-exists", (
        f'Expected "type" to be "https://my-api-doc.dev/problems/user-already-exists". Body: {body}'
    )
