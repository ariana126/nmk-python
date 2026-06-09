Feature: Vitals Recording
  As a clinic member
  I want to record a patient's vitals
  So that I can access them in the future

  Background:
    Given the application is running
    And I am logged in as a clinic member
    And a patient exists with ID "patient-id"

  Scenario: Successful vitals recording
    When I record vitals for the patient with ID "patient-id" with the following details:
      | heartRatePerMinute | 100  |
      | systolicBp         | 130  |
      | temperature        | 36.5 |
    Then the response status should be 201
    And I should see a new record at the top of the patient's vitals with the following details:
      | heartRatePerMinute | 100             |
      | systolicBp         | 130             |
      | temperature        | 36.5            |
      | recordedAt         | <past-datetime> |

  Scenario: Recording for a non-existent patient
    When I record vitals for the patient with ID "not-existent-id" with the following details:
      | heartRatePerMinute | 100  |
      | systolicBp         | 130  |
      | temperature        | 36.5 |
    Then the response status should be 404
    And the response should be a valid problem detail

  Scenario: Recording with missing required fields
    When I record vitals for the patient with ID "patient-id" with the following details:
      | heartRatePerMinute | 100  |
    Then the response status should be 400
    And the response should be a valid problem detail
    And the response body should contain validation errors for:
      | systolicBp  |
      | temperature |

  Scenario: Unauthenticated access is rejected
    When I log out of my account
    And I record vitals for the patient with ID "patient-id" with the following details:
      | heartRatePerMinute | 100  |
      | systolicBp         | 130  |
      | temperature        | 36.5 |
    Then the response status should be 401
    And the response should be a valid problem detail

  Scenario: Recording with an invalid heart rate
    When I record vitals for the patient with ID "patient-id" with the following details:
      | heartRatePerMinute | -1   |
      | systolicBp         | 130  |
      | temperature        | 36.5 |
    Then the response status should be 400
    And the response should be a valid problem detail
    And the response body should contain validation errors for:
      | heartRatePerMinute |

  Scenario: Recording with an invalid systolic blood pressure
    When I record vitals for the patient with ID "patient-id" with the following details:
      | heartRatePerMinute | 100  |
      | systolicBp         | -1   |
      | temperature        | 36.5 |
    Then the response status should be 400
    And the response should be a valid problem detail
    And the response body should contain validation errors for:
      | systolicBp |

  Scenario: Recording with an invalid temperature
    When I record vitals for the patient with ID "patient-id" with the following details:
      | heartRatePerMinute | 100 |
      | systolicBp         | 130 |
      | temperature        | -1  |
    Then the response status should be 400
    And the response should be a valid problem detail
    And the response body should contain validation errors for:
      | temperature |