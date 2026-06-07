from pytest_bdd import given, then, parsers


@given("the application is running")
def application_is_running(client):
    pass


@then(parsers.parse("the response status should be {status_code:d}"))
def response_status_should_be(context, status_code):
    response = context["response"]
    assert response.status_code == status_code, (
        f"Expected HTTP {status_code} but got {response.status_code}. "
        f"Body: {response.json()}"
    )


@then("the response should be a valid problem detail")
def response_should_be_valid_problem_detail(context):
    response = context["response"]
    content_type = response.headers.get("content-type", "")
    assert "application/problem+json" in content_type, (
        f'Expected Content-Type to include "application/problem+json" but got "{content_type}"'
    )

    body = response.json()
    type_val = body.get("type", "")
    prefix = "https://my-api-doc.dev/problems/"
    assert type_val == "about:blank" or (
        type_val.startswith(prefix) and len(type_val) > len(prefix)
    ), f'Expected "type" to be "about:blank" or "{prefix}<uri>". Body: {body}'
    assert isinstance(body.get("title"), str) and len(body["title"]) > 0, (
        f'Expected "title" to be a non-empty string. Body: {body}'
    )
    assert body.get("status") == response.status_code, (
        f'Expected body "status" to match HTTP status {response.status_code}. Body: {body}'
    )


@then("the response body should contain validation errors for:")
def response_body_should_contain_validation_errors_for(context, datatable):
    body = context["response"].json()
    assert body.get("type") == "https://my-api-doc.dev/problems/validation-error", (
        f'Expected "type" to be "https://my-api-doc.dev/problems/validation-error". Body: {body}'
    )
    errors = body.get("errors")
    assert isinstance(errors, list), f'Expected "errors" to be a list. Body: {body}'
    for row in datatable:
        field = row[0]
        field_present = any(err.get("field") == field for err in errors)
        assert field_present, (
            f'Expected a validation error for field "{field}" but got: {errors}'
        )
