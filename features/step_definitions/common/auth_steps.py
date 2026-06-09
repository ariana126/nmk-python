from pytest_bdd import given, when

_CLINIC_MEMBER_EMAIL = "clinic.member@example.com"
_CLINIC_MEMBER_PASSWORD = "ClinicPass123!"


@given("I am logged in as a clinic member")
def logged_in_as_clinic_member(client, context):
    client.post(
        "/api/users",
        json={
            "firstName": "Clinic",
            "lastName": "Member",
            "email": _CLINIC_MEMBER_EMAIL,
            "password": _CLINIC_MEMBER_PASSWORD,
        },
    )
    response = client.post(
        "/api/auth/login",
        json={"email": _CLINIC_MEMBER_EMAIL, "password": _CLINIC_MEMBER_PASSWORD},
    )
    assert response.status_code == 200
    context["accessToken"] = response.json()["accessToken"]


@when("I log out of my account")
def log_out_of_account(context):
    context.pop("accessToken", None)
