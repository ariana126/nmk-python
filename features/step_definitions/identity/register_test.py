import pytest
from pytest_bdd import scenarios, given, when, then, parsers

scenarios("../../specs/identity/register.feature")


@given(parsers.parse('no user with email "{email}" exists'))
def no_user_with_email_exists(email):
    pass


@given(parsers.parse('a user with email "{email}" already exists'))
def a_user_with_email_already_exists(client, email):
    response = client.post("/users", json={
        "firstName": "Existing",
        "lastName": "User",
        "email": email,
        "password": "ExistingPass123!",
    })
    assert response.status_code == 201


@when("I register with the following details:")
def register_with_details(context, client, datatable):
    data = {row[0]: row[1] for row in datatable}
    context["response"] = client.post("/users", json=data)


@then(parsers.parse('I should be able to log in with email "{email}" and password "{password}"'))
def should_be_able_to_log_in(context, client, email, password):
    response = client.post("/auth/tokens", json={"email": email, "password": password})
    assert response.status_code == 200
    context["token"] = response.json()["token"]


@then("I should see my profile with the following details:")
def should_see_profile_with_details(context, client, datatable):
    response = client.get("/users/me", headers={"Authorization": f"Bearer {context['token']}"})
    assert response.status_code == 200
    body = response.json()
    for row in datatable:
        field, expected = row[0], row[1]
        if expected == "<present>":
            assert field in body, f"Expected field '{field}' to be present in profile"
        else:
            assert body[field] == expected, f"Expected profile['{field}'] == '{expected}', got '{body.get(field)}'"


@then(parsers.parse('I should not be able to log in with email "{email}" and password "{password}"'))
def should_not_be_able_to_log_in(client, email, password):
    response = client.post("/auth/tokens", json={"email": email, "password": password})
    assert response.status_code in (401, 403)
