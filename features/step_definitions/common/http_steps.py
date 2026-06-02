import pytest
from pytest_bdd import given, then, parsers


@given("the application is running")
def application_is_running(client):
    pass


@then(parsers.parse("the response status should be {status_code:d}"))
def response_status_should_be(context, status_code):
    assert context["response"].status_code == status_code


@then("the response should be a valid problem detail")
def response_should_be_valid_problem_detail(context):
    body = context["response"].json()
    assert "status" in body
    assert "title" in body


@then("the response body should contain validation errors for:")
def response_body_should_contain_validation_errors_for(context, datatable):
    body_str = str(context["response"].json())
    for row in datatable:
        field = row[0]
        assert field in body_str, f"Expected validation error for field '{field}' in response body"
